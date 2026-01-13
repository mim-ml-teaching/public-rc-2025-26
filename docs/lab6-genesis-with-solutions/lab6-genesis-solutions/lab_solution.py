import numpy as np
import genesis as gs
import torch
from typing import List, Tuple, Any


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

    scene.build()

    # Now, move boxes to random positions.
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
            position=[position[0], position[1], BOX_SIZE / 2],
        )

    # Set gripper gains
    gripper.set_dofs_kp(np.array([500, 500, 500])) # x, y, z
    gripper.set_dofs_kv(np.array([50, 50, 50]))

    return scene, gripper, boxes


def get_furthest_box_position(boxes: List[Any]) -> Tuple[torch.Tensor, torch.Tensor]:
    all_boxes_pos = torch.stack([box.get_dofs_position()[:3] for box in boxes]) # (N_BOXES, 3)
    
    distances = torch.norm(all_boxes_pos[:, :2], dim=1) # (N_BOXES)
    
    max_distance, box_index = torch.max(distances, dim=0)
    
    box_position = all_boxes_pos[box_index]

    return box_position, max_distance


def get_position_sequence_to_move_box(gripper: Any, box_position: torch.Tensor) -> List[torch.Tensor]:
    g_x_y = gripper.get_dofs_position()[:2]
    g_x, g_y = g_x_y[0], g_x_y[1]
    b_x_y = box_position[:2]
    b_x, b_y = b_x_y[0], b_x_y[1]

    # Move point along the vector (b_x, b_y) away from (0, 0)
    # https://math.stackexchange.com/a/333363
    HOW_FAR_TO_PUSH_FROM = 0.4
    norm = torch.norm(b_x_y)
    start_x_y = b_x_y + b_x_y / norm * HOW_FAR_TO_PUSH_FROM
    start_x, start_y = start_x_y[0], start_x_y[1]

    position_sequence = []
    z_high = torch.tensor(BOX_SIZE + 0.1, device=box_position.device)
    z_low = torch.tensor(BOX_SIZE / 2, device=box_position.device)

    position_sequence.append(torch.stack([g_x, g_y, z_high]))
    position_sequence.append(torch.stack([start_x, start_y, z_high]))
    position_sequence.append(torch.stack([start_x, start_y, z_low]))
    position_sequence.append(torch.stack([b_x, b_y, z_low]))
    
    return position_sequence


if __name__ == "__main__":

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    scene, gripper, boxes = create_environment(device=device)

    while True:
        box_position, max_distance = get_furthest_box_position(boxes=boxes)
        
        # Stop if the furthest box is close enough
        if max_distance <= DISTANCE_FROM_CENTER_TO_PASS:
            break
        
        # Do one sequence
        position_sequence = get_position_sequence_to_move_box(gripper=gripper, box_position=box_position)
        for position in position_sequence:
            gripper.control_dofs_position(position)
            for _ in range(40):
                scene.step()
