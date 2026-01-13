# plotting.py
import numpy as np
import matplotlib
matplotlib.use("Agg")  # fixes mac OS issue  
import matplotlib.pyplot as plt

def plot_results(pnp_position_list, true_position_list, kalman_position_list, filename="plot_results.png"):
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    dim_names = ['X', 'Y', 'Z']
    
    if pnp_position_list and true_position_list and kalman_position_list:
        pnp_position_array = np.array(pnp_position_list)
        gate_position_array = np.array(true_position_list)
        kf_filtered_array = np.array(kalman_position_list)
        
        for dim in range(3):
            ax = axes[dim]
            iterations = np.arange(len(pnp_position_array))
            ax.plot(iterations, pnp_position_array[:, dim], linestyle='-', label='PnP position (estimate)', alpha=0.7, linewidth=1.5)
            ax.plot(iterations, gate_position_array[:, dim], linestyle='-', label='True position (ground truth)', alpha=0.7, linewidth=1.5)
            ax.plot(iterations, kf_filtered_array[:, dim], linestyle='-', label='Kalman position (filtered)', alpha=0.7, linewidth=1.5)
            ax.set_xlabel("Iteration")
            ax.set_ylabel(f"{dim_names[dim]} Position (m)")
            ax.set_title(f"{dim_names[dim]} Dimension: PnP vs True Position vs Kalman Filter")
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        plt.tight_layout()
        plt.savefig(filename, dpi=300)
        plt.close()
        print(f"Saved plot to {filename}")