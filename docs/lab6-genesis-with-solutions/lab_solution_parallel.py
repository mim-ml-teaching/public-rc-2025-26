import numpy as np
import torch
import genesis as gs
from typing import List, Tuple, Any


ENVS_NUMBER = 4
BOXES_NUMBER = 4
BOX_SIZE = 0.2
DISTANCE_FROM_CENTER_TO_PASS = 0.4


def create_environment(device: str) -> Tuple[gs.Scene, Any, List[Any]]:
    # Initialize genesis
    gs.init(backend=gs.cpu if device == 'cpu' else gs.gpu)

    # Create scene
    scene = gs.Scene(
        sim_options=gs.options.SimOptions(
            dt=0.01,
        ),
        viewer_options=gs.options.ViewerOptions(
            camera_pos=(2, -2, 2),
            camera_lookat=(0.0, 0.0, 0.0),
            camera_fov=30,
            max_FPS=60,
        ),
        show_viewer=True,
    )

    # Add floor
    scene.add_entity(
        gs.morphs.Plane(
            pos=(0, 0, 0)
        )
    )

    # Add target visualization
    scene.add_entity(
        gs.morphs.Cylinder(
            radius=DISTANCE_FROM_CENTER_TO_PASS,
            height=0.002,
            pos=(0, 0, 0),
            collision=False,
            fixed=True
        ),
        surface=gs.surfaces.Default(color=(0, 0.5, 0, 0.5)),
    )

    # Add gripper
    gripper = scene.add_entity(
        gs.morphs.MJCF(file='gripper.xml')
    )

    # Add boxes. Position does not matter for now.
    boxes = []
    for i in range(BOXES_NUMBER):
        box = scene.add_entity(
            gs.morphs.Box(
                pos=(0, (i + 1) * BOX_SIZE, BOX_SIZE / 2),
                size=(BOX_SIZE, BOX_SIZE, BOX_SIZE)
            ),
            material=gs.materials.Rigid(
                rho=100.0, 
                friction=1.0
            ),
            surface=gs.surfaces.Default(
                color=(1, 0, 0, 1)
            ),
        )
        boxes.append(box)

    scene.build(n_envs=ENVS_NUMBER, env_spacing=(3.0, 3.0))

    # Now, for each environment move boxes to random positions.
    for env_id in range(ENVS_NUMBER):
        positions = []
        while len(positions) < BOXES_NUMBER:
            candidate = np.random.uniform(-1, 1, size=2)

            if np.linalg.norm(candidate) <= DISTANCE_FROM_CENTER_TO_PASS:
                continue
                
            if positions:
                distances = np.abs(np.array(positions) - candidate)
                if np.any(np.all(distances <= BOX_SIZE, axis=1)):
                    continue
            
            positions.append(candidate)
        
        for box, position in zip(boxes, positions):
            box.set_dofs_position(
                dofs_idx_local=[0,1,2], # Change only x,y,z
                position=[[position[0], position[1], BOX_SIZE / 2]],
                envs_idx=[env_id]
            )

    # Set gripper gains
    gripper.set_dofs_kp(np.array([500, 500, 500])) # x, y, z
    gripper.set_dofs_kv(np.array([50, 50, 50]))

    return scene, gripper, boxes


def get_furthest_box_position(boxes: List[Any]) -> Tuple[torch.Tensor, torch.Tensor]:
    all_boxes_pos = torch.stack([box.get_dofs_position()[:, :3] for box in boxes]) # (N_BOXES, ENVS_NUMBER, 3)
    
    distances = torch.norm(all_boxes_pos[:, :, :2], dim=2) # (N_BOXES, ENVS_NUMBER)
    
    max_distances, box_indices = torch.max(distances, dim=0) # (ENVS_NUMBER), (ENVS_NUMBER)

    env_indices = torch.arange(all_boxes_pos.shape[1], device=all_boxes_pos.device)
    boxes_positions = all_boxes_pos[box_indices, env_indices, :] # (ENVS_NUMBER, 3)

    return boxes_positions, max_distances


def get_position_sequence_to_move_box(gripper: Any, boxes_positions: torch.Tensor) -> List[torch.Tensor]:
    g_x_y = gripper.get_dofs_position()[:, :2] # (ENVS_NUMBER, 2)
    g_x, g_y = g_x_y[:, 0], g_x_y[:, 1]
    b_x_y = boxes_positions[:, :2] # (ENVS_NUMBER, 2)
    b_x, b_y = b_x_y[:, 0], b_x_y[:, 1]

    # Move point along the vector (b_x, b_y) away from (0, 0)
    # https://math.stackexchange.com/a/333363
    HOW_FAR_TO_PUSH_FROM = 0.4
    norm = torch.norm(b_x_y, dim=1, keepdim=True) # (ENVS_NUMBER, 1)
    start_x_y = b_x_y + b_x_y / norm * HOW_FAR_TO_PUSH_FROM
    start_x, start_y = start_x_y[:, 0], start_x_y[:, 1]

    position_sequence = []
    z_high = torch.full((len(b_x),), BOX_SIZE + 0.1, device=boxes_positions.device)
    z_low = torch.full((len(b_x),), BOX_SIZE / 2, device=boxes_positions.device)
    position_sequence.append(torch.stack([g_x, g_y, z_high], dim=1)) # (ENVS_NUMBER, 3)
    position_sequence.append(torch.stack([start_x, start_y, z_high], dim=1))
    position_sequence.append(torch.stack([start_x, start_y, z_low], dim=1))
    position_sequence.append(torch.stack([b_x, b_y, z_low], dim=1))
    
    return position_sequence


if __name__ == "__main__":

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    scene, gripper, boxes = create_environment(device=device)

    while True:
        boxes_positions, max_distances = get_furthest_box_position(boxes=boxes)
        
        # Stop if all envs finished
        if torch.all(max_distances <= DISTANCE_FROM_CENTER_TO_PASS):
            break
        
        # Do one sequence in all envs
        position_sequence = get_position_sequence_to_move_box(gripper=gripper, boxes_positions=boxes_positions)
        for position in position_sequence:
            gripper.control_dofs_position(position)
            for _ in range(40):
                scene.step()
