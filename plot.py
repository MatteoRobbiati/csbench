#!/usr/bin/env python
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from csbench.ui.extract import extract_simulation_results

import matplotlib.pyplot as plt
import numpy as np

def plot_fidelity_vs_bond_dim(df, num_qubits=35, num_layers=10):
    # 1. Filter the dataset
    mask = (df['qubits'] == num_qubits) & (df['layers'] == num_layers)
    plot_df = df[mask].copy()
    
    if plot_df.empty:
        print(f"No data found for qubits={num_qubits} and layers={num_layers}")
        return

    plt.figure(figsize=(10, 6))
    
    # --- Process MPSTAB ---
    mp_df = plot_df[plot_df['engine'] == 'mpstab']
    if not mp_df.empty:
        # Get unique bond dimensions
        bond_dims = sorted(mp_df['max_bond_dimension'].unique())
        
        # Calculate min and max for the shaded area (across all repl_prob and seeds)
        mp_grouped = mp_df.groupby('max_bond_dimension')['fidelity_median']
        mins = mp_grouped.min()
        maxs = mp_grouped.max()
        
        # Draw the shaded area
        plt.fill_between(mins.index, mins, maxs, color='blue', alpha=0.15, label='mpstab range')
        
        # Draw individual lines for each replacement probability (light)
        for prob in mp_df['repl_prob'].unique():
            prob_data = mp_df[mp_df['repl_prob'] == prob].sort_values('max_bond_dimension')
            # Averaging seeds if multiple exist for same prob/bond_dim
            avg_prob_data = prob_data.groupby('max_bond_dimension')['fidelity_median'].mean()
            plt.plot(avg_prob_data.index, avg_prob_data.values, 
                     color='blue', alpha=0.3, linewidth=1, linestyle='--')

    # --- Process TENSOR NETWORK ---
    tn_df = plot_df[plot_df['engine'] == 'tensor_network']
    if not tn_df.empty:
        # Average across seeds/probs if they exist
        tn_avg = tn_df.groupby('max_bond_dimension')['fidelity_median'].mean().sort_values()
        plt.plot(tn_avg.index, tn_avg.values, color='red', marker='o', 
                 linewidth=2, label='tensor_network (avg)')

    # Formatting
    plt.title(f"Fidelity vs Max Bond Dimension (Qubits: {num_qubits}, Layers: {num_layers})")
    plt.xlabel("Max Bond Dimension")
    plt.ylabel("Fidelity (Median)")
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.legend()
    
    # Save the plot
    plt.savefig("plots/fidelity_plot.png")



def plot_time_scaling(df, num_qubits=35, bond_dim=8):
    # 1. Filter the dataset for fixed qubits and bond dimension
    mask = (df['qubits'] == num_qubits) & (df['max_bond_dimension'] == bond_dim)
    plot_df = df[mask].copy()
    
    if plot_df.empty:
        print(f"No data found for qubits={num_qubits} and bond_dim={bond_dim}")
        return

    plt.figure(figsize=(10, 6))

    def normalize_series(series):
        # Normalizes by the value at the minimum number of layers
        if series.empty: return series
        return series / series.iloc[0]

    # --- Process MPSTAB ---
    mp_df = plot_df[plot_df['engine'] == 'mpstab']
    if not mp_df.empty:
        # We need to store normalized values for each repl_prob to find min/max range
        normalized_probs = []
        
        # Sort by layers to ensure normalization uses the correct baseline
        mp_df = mp_df.sort_values('layers')
        
        for prob in mp_df['repl_prob'].unique():
            prob_data = mp_df[mp_df['repl_prob'] == prob]
            # Average seeds for this specific prob/layer combination
            avg_time = prob_data.groupby('layers')['execution_time_median'].mean()
            
            # Normalize by the first layer value
            norm_time = normalize_series(avg_time)
            normalized_probs.append(norm_time)
            
            # Plot individual light lines
            plt.plot(norm_time.index, norm_time.values, 
                     color='blue', alpha=0.2, linewidth=1, linestyle='--')

        # Calculate the envelope for the shaded area
        all_norm_df = pd.concat(normalized_probs, axis=1)
        mins = all_norm_df.min(axis=1)
        maxs = all_norm_df.max(axis=1)
        
        plt.fill_between(mins.index, mins, maxs, color='blue', alpha=0.1, label='mpstab scaling range')

    # --- Process TENSOR NETWORK ---
    tn_df = plot_df[plot_df['engine'] == 'tensor_network'].sort_values('layers')
    if not tn_df.empty:
        tn_avg = tn_df.groupby('layers')['execution_time_median'].mean()
        tn_norm = normalize_series(tn_avg)
        plt.plot(tn_norm.index, tn_norm.values, color='red', marker='s', 
                 linewidth=2, label='tensor_network scaling')

    # Formatting
    plt.title(f"Time Scaling vs Layers (Qubits: {num_qubits}, Bond Dim: {bond_dim})")
    plt.xlabel("Number of Layers")
    plt.ylabel("Relative Time Scaling (T / T_min_layers)")
    plt.yscale('log')  # Often useful for scaling plots
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.legend()
    
    plt.savefig("plots/time_scaling_plot.png")


import matplotlib.pyplot as plt
import numpy as np

def plot_time_vs_repl_prob(df, num_qubits=35, num_layers=10, bond_dim=8):
    # 1. Filter dataset for fixed parameters
    mask = (df['qubits'] == num_qubits) & \
           (df['layers'] == num_layers) & \
           (df['max_bond_dimension'] == bond_dim)
    plot_df = df[mask].copy()
    
    if plot_df.empty:
        print(f"No data for Q={num_qubits}, L={num_layers}, BD={bond_dim}")
        return

    plt.figure(figsize=(10, 6))

    # --- Process MPSTAB ---
    mp_df = plot_df[plot_df['engine'] == 'mpstab'].sort_values('repl_prob')
    
    if not mp_df.empty:
        # Baseline for normalization: median time at the smallest replacement probability
        min_prob = mp_df['repl_prob'].min()
        baseline_time = mp_df[mp_df['repl_prob'] == min_prob]['execution_time_median'].mean()
        
        # Group by probability to handle multiple seeds
        grouped = mp_df.groupby('repl_prob')['execution_time_median']
        
        # Calculate scaling and bounds
        means = grouped.mean() / baseline_time
        mins = grouped.min() / baseline_time
        maxs = grouped.max() / baseline_time
        
        # Plot mean line and shaded area for seeds
        plt.plot(means.index, means.values, color='blue', marker='o', label='mpstab scaling')
        plt.fill_between(means.index, mins, maxs, color='blue', alpha=0.15, label='seed variance')

    # Formatting
    plt.title(f"Time Scaling vs Replacement Probability\n(Qubits: {num_qubits}, Layers: {num_layers}, Bond Dim: {bond_dim})")
    plt.xlabel("Replacement Probability")
    plt.ylabel("Relative Time Scaling ($T / T_{prob_{min}}$)")
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.legend()
    
    plt.savefig("plots/time_vs_repl_prob_plot.png")

def main():
    data_frame = extract_simulation_results("/home/mattiaro/csbench/results/hardware_efficient_central_x/")
    # plot_fidelity_vs_bond_dim(data_frame)
    # plot_time_scaling(data_frame, num_qubits=35, bond_dim=16)
    plot_time_vs_repl_prob(data_frame, num_qubits=35, num_layers=10, bond_dim=8)

if __name__ == "__main__":
    main()
