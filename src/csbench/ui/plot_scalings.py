"""Plotting utilities for scaling analysis of quantum circuit benchmarks."""

import json
import re
from pathlib import Path
from collections import defaultdict

import numpy as np
import matplotlib.pyplot as plt


def parse_results_directory(results_dir: str | Path) -> dict:
    """
    Parse all results from the results directory structure.

    Returns a dictionary with structure:
    {
        'engine_name': {
            'repl_prob': {
                'nqubits': [execution_times],
                ...
            },
            ...
        },
        ...
    }
    """
    results_dir = Path(results_dir)
    data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    # Recursively find all results_*.json files
    for results_file in results_dir.rglob("results_*.json"):
        # Extract nqubits and repl_prob from the path
        path_parts = results_file.parts

        # Find the part matching "qubits{N}_layers{L}_repl_prob{P}..."
        nqubits = None
        repl_prob = None
        for part in path_parts:
            nqubits_match = re.match(r"qubits(\d+)_", part)
            repl_prob_match = re.search(r"repl_prob([\d.]+)", part)

            if nqubits_match:
                nqubits = int(nqubits_match.group(1))
            if repl_prob_match:
                repl_prob = float(repl_prob_match.group(1))

        if nqubits is None or repl_prob is None:
            continue

        # Find the engine config part (between qubits{N}... and results_...)
        # It's typically like "statevector_qibojit_sparse" or "mpstab_max_bond_dimension32_sparse"
        engine_config = results_file.parent.name

        # Parse the results JSON
        with open(results_file, "r") as f:
            results = json.load(f)

        # Extract execution times
        execution_times = [
            execution["execution_time_seconds"] for execution in results["executions"]
        ]

        data[engine_config][repl_prob][nqubits].extend(execution_times)

    return dict(data)


def parse_results_with_fidelity(results_dir: str | Path) -> dict:
    """
    Parse all results including fidelities from the results directory structure.

    Returns a dictionary with structure:
    {
        'engine_name': {
            'repl_prob': {
                'nqubits': {
                    'execution_times': [times],
                    'fidelities': [fidelities],
                    'bond_dimension': int (if applicable)
                },
                ...
            },
            ...
        },
        ...
    }
    """
    results_dir = Path(results_dir)
    data = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(
                lambda: {
                    "execution_times": [],
                    "fidelities": [],
                    "bond_dimension": None,
                }
            )
        )
    )

    # Recursively find all results_*.json files
    for results_file in results_dir.rglob("results_*.json"):
        # Extract nqubits and repl_prob from the path
        path_parts = results_file.parts

        # Find the part matching "qubits{N}_layers{L}_repl_prob{P}..."
        nqubits = None
        repl_prob = None
        for part in path_parts:
            nqubits_match = re.match(r"qubits(\d+)_", part)
            repl_prob_match = re.search(r"repl_prob([\d.]+)", part)

            if nqubits_match:
                nqubits = int(nqubits_match.group(1))
            if repl_prob_match:
                repl_prob = float(repl_prob_match.group(1))

        if nqubits is None or repl_prob is None:
            continue

        # Find the engine config part
        engine_config = results_file.parent.name

        # Extract bond dimension if present
        bond_dim_match = re.search(r"max_bond_dimension(\d+)", engine_config)
        bond_dimension = int(bond_dim_match.group(1)) if bond_dim_match else None

        # Parse the results JSON
        with open(results_file, "r") as f:
            results = json.load(f)

        # Extract execution times and fidelities
        execution_times = []
        fidelities = []
        for execution in results["executions"]:
            execution_times.append(execution["execution_time_seconds"])
            fidelities.append(execution["fidelity"])

        data[engine_config][repl_prob][nqubits]["execution_times"].extend(
            execution_times
        )
        data[engine_config][repl_prob][nqubits]["fidelities"].extend(fidelities)
        if bond_dimension is not None:
            data[engine_config][repl_prob][nqubits]["bond_dimension"] = bond_dimension

    return dict(data)


def marginalize_over_repl_prob(data: dict) -> dict:
    """
    Marginalize the data over replacement probability values.

    Takes data structure:
    {
        'engine_name': {
            'repl_prob': {
                'nqubits': [times],
                ...
            },
            ...
        },
        ...
    }

    Returns aggregated data:
    {
        'engine_name': {
            'nqubits': [times],
            ...
        },
        ...
    }
    """
    marginalized = defaultdict(lambda: defaultdict(list))

    for engine_name, repl_prob_dict in data.items():
        for repl_prob, qubit_dict in repl_prob_dict.items():
            for nqubits, times in qubit_dict.items():
                marginalized[engine_name][nqubits].extend(times)

    return dict(marginalized)


def get_repl_probs(data: dict) -> list:
    """
    Extract all unique replacement probability values from the data.

    Returns a sorted list of replacement probabilities.
    """
    repl_probs = set()
    for engine_data in data.values():
        repl_probs.update(engine_data.keys())
    return sorted(repl_probs)


def get_engines(data: dict) -> list:
    """
    Extract all unique engine configurations from the data.

    Returns a sorted list of engine names.
    """
    return sorted(data.keys())


def extract_bond_dimension(engine_name: str) -> int | None:
    """
    Extract the bond dimension from an engine name.

    Parameters
    ----------
    engine_name : str
        Engine name, e.g., "mpstab_sparse_max_bond_dimension32"

    Returns
    -------
    int or None
        The bond dimension if found, otherwise None
    """
    match = re.search(r"max_bond_dimension(\d+)", engine_name)
    return int(match.group(1)) if match else None


def get_marker_for_simulator(simulator_type: str) -> str:
    """
    Get a marker style for a specific simulator type.

    Parameters
    ----------
    simulator_type : str
        The simulator type, e.g., "StateVector (qibojit)"

    Returns
    -------
    str
        Marker symbol
    """
    marker_map = {
        "StateVector (qibojit)": "o",  # Circle
        "StateVector (numpy)": "s",  # Square
        "MPS (mpstab)": "^",  # Triangle up
    }
    return marker_map.get(simulator_type, "o")


def filter_engines_for_plotting(engines: list) -> list:
    """
    Filter engines for plotting, removing sparse variants of mpstab.

    Sparse matrices only make sense for statevector engines.
    For mpstab, we remove the "_sparse" suffix.

    Parameters
    ----------
    engines : list
        List of engine names

    Returns
    -------
    list
        Filtered engine names
    """
    filtered = []
    for engine in engines:
        # For mpstab, remove _sparse from the name since it doesn't make sense
        if "mpstab" in engine and "_sparse" in engine:
            # Replace mpstab_sparse with mpstab
            cleaned_engine = engine.replace("_sparse", "")
            if cleaned_engine not in filtered:
                filtered.append(cleaned_engine)
        else:
            filtered.append(engine)

    return filtered


def get_engine_color_map(engines: list) -> dict:
    """
    Create a color map for different simulators with different styles for sparse/dense.

    Parameters
    ----------
    engines : list
        List of engine names

    Returns
    -------
    dict
        Dictionary mapping engine names to colors and styles
    """
    # Define base colors for different simulator types
    base_colors = {
        "statevector_qibojit": "#1f77b4",  # Blue
        "statevector_numpy": "#2ca02c",  # Green
        "mpstab": "#ff7f0e",  # Orange
    }

    # Create color map considering sparse/dense
    color_map = {}
    for engine in engines:
        # Find the base simulator type
        if "statevector_qibojit" in engine:
            base_color = base_colors["statevector_qibojit"]
            simulator = "StateVector (qibojit)"
        elif "statevector_numpy" in engine:
            base_color = base_colors["statevector_numpy"]
            simulator = "StateVector (numpy)"
        elif "mpstab" in engine:
            base_color = base_colors["mpstab"]
            simulator = "MPS (mpstab)"
        else:
            base_color = "#1f77b4"
            simulator = engine

        # Adjust transparency/shade for sparse vs dense
        is_sparse = "sparse" in engine
        linestyle = "-" if is_sparse else "--"

        color_map[engine] = {
            "color": base_color,
            "linestyle": linestyle,
            "simulator": simulator,
            "matrix_type": "Sparse" if is_sparse else "Dense",
        }

    return color_map


def filter_engines_by_max_bond(engines: list, max_bond_dim: int = None) -> list:
    """
    Filter engines to get only those matching a specific max bond dimension.

    Parameters
    ----------
    engines : list
        List of engine names
    max_bond_dim : int, optional
        Maximum bond dimension to filter by (e.g., 32). If None, return all engines.

    Returns
    -------
    list
        Filtered engine names
    """
    if max_bond_dim is None:
        return engines

    filtered = []
    for engine in engines:
        if max_bond_dim is None or f"max_bond_dimension{max_bond_dim}" in engine:
            filtered.append(engine)

    return filtered


def filter_repl_probs(data: dict, selected_repl_probs: list = None) -> dict:
    """
    Filter data to only include selected replacement probabilities.

    Parameters
    ----------
    data : dict
        The full data structure
    selected_repl_probs : list, optional
        List of replacement probabilities to include. If None, include all.

    Returns
    -------
    dict
        Filtered data structure
    """
    if selected_repl_probs is None:
        return data

    filtered = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for engine_name, repl_prob_dict in data.items():
        for repl_prob, qubit_dict in repl_prob_dict.items():
            if repl_prob in selected_repl_probs:
                filtered[engine_name][repl_prob] = qubit_dict

    return dict(filtered)


def plot_scaling_marginalized(
    results_dir: str | Path,
    selected_repl_probs: list = None,
    max_bond_dim: int = None,
    output_path: str | Path = None,
) -> plt.Figure:
    """
    Plot execution times vs. number of qubits for different engines, marginalized over replacement probability.

    Parameters
    ----------
    results_dir : str or Path
        Path to the results directory containing benchmark results.
    selected_repl_probs : list, optional
        List of replacement probabilities to include. If None, include all.
    max_bond_dim : int, optional
        Maximum bond dimension to filter by (e.g., 32). If None, include all.
    output_path : str or Path, optional
        If provided, save the figure to this path.

    Returns
    -------
    plt.Figure
        The matplotlib figure object.
    """
    # Parse results
    raw_data = parse_results_directory(results_dir)

    if not raw_data:
        raise ValueError(f"No results found in {results_dir}")

    # Filter by replacement probability
    filtered_data = filter_repl_probs(raw_data, selected_repl_probs)

    # Filter by max bond dimension
    all_engines = get_engines(filtered_data)
    filtered_engines = filter_engines_by_max_bond(all_engines, max_bond_dim)

    filtered_data = {
        engine: filtered_data[engine]
        for engine in filtered_engines
        if engine in filtered_data
    }

    # Marginalize over replacement probability
    data = marginalize_over_repl_prob(filtered_data)

    # Get color mapping
    color_map = get_engine_color_map(list(data.keys()))

    # Prepare data for plotting
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot for each engine
    for engine_name, qubit_data in sorted(data.items()):
        # Sort by qubit count
        qubits = sorted(qubit_data.keys())

        # Calculate statistics
        means = []
        sems = []

        for n in qubits:
            times = np.array(qubit_data[n])
            means.append(np.mean(times))
            sems.append(np.std(times) / np.sqrt(len(times)))

        # Get styling
        style = color_map[engine_name]
        label = f"{style['simulator']} ({style['matrix_type']})"

        ax.errorbar(
            qubits,
            means,
            yerr=sems,
            marker="o",
            linestyle=style["linestyle"],
            linewidth=2,
            label=label,
            color=style["color"],
            capsize=5,
            capthick=2,
        )

    # Labels and formatting
    ax.set_xlabel("Number of Qubits", fontsize=12, fontweight="bold")
    ax.set_ylabel("Execution Time (seconds)", fontsize=12, fontweight="bold")

    title = "Quantum Circuit Execution Time Scaling (Marginalized over Replacement Probability)"
    if selected_repl_probs:
        title += f"\np ∈ {selected_repl_probs}"
    if max_bond_dim:
        title += f", D={max_bond_dim}"

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.legend(fontsize=11, loc="best")
    ax.grid(True, alpha=0.3)
    ax.set_yscale("log")

    fig.tight_layout()

    # Save if output path provided
    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig


def plot_scaling_per_repl_prob(
    results_dir: str | Path,
    selected_repl_probs: list = None,
    max_bond_dim: int = None,
    output_path: str | Path = None,
) -> plt.Figure:
    """
    Plot execution times vs. number of qubits for different engines, with separate curves per replacement probability.

    Parameters
    ----------
    results_dir : str or Path
        Path to the results directory containing benchmark results.
    selected_repl_probs : list, optional
        List of replacement probabilities to include. If None, include all.
    max_bond_dim : int, optional
        Maximum bond dimension to filter by (e.g., 32). If None, include all.
    output_path : str or Path, optional
        If provided, save the figure to this path.

    Returns
    -------
    plt.Figure
        The matplotlib figure object.
    """
    # Parse results
    raw_data = parse_results_directory(results_dir)

    if not raw_data:
        raise ValueError(f"No results found in {results_dir}")

    # Filter by replacement probability
    data = filter_repl_probs(raw_data, selected_repl_probs)

    # Filter by max bond dimension
    all_engines = get_engines(data)
    filtered_engines = filter_engines_by_max_bond(all_engines, max_bond_dim)

    data = {engine: data[engine] for engine in filtered_engines if engine in data}

    repl_probs = get_repl_probs(data)

    if not repl_probs:
        raise ValueError("No data found matching the selected filters")

    # Get unique engines
    engines = sorted(data.keys())

    # Get color mapping for engines
    color_map = get_engine_color_map(engines)

    # Define colors for different replacement probabilities
    colors_repl = plt.cm.Spectral(np.linspace(0, 1, len(repl_probs)))

    # Prepare data for plotting
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot for each engine and replacement probability
    for engine_name in engines:
        engine_data = data[engine_name]
        engine_style = color_map[engine_name]

        for repl_idx, repl_prob in enumerate(repl_probs):
            if repl_prob not in engine_data:
                continue

            qubit_data = engine_data[repl_prob]
            qubits = sorted(qubit_data.keys())

            # Calculate statistics
            means = []
            sems = []

            for n in qubits:
                times = np.array(qubit_data[n])
                means.append(np.mean(times))
                sems.append(np.std(times) / np.sqrt(len(times)))

            # Create label combining engine and replacement probability
            label = f"{engine_style['simulator']} ({engine_style['matrix_type']}) p={repl_prob:.2f}"

            ax.errorbar(
                qubits,
                means,
                yerr=sems,
                marker="o",
                linestyle=engine_style["linestyle"],
                linewidth=2,
                label=label,
                color=colors_repl[repl_idx],
                capsize=5,
                capthick=2,
                alpha=0.7 + 0.3 * (repl_idx / len(repl_probs)),
            )

    # Labels and formatting
    ax.set_xlabel("Number of Qubits", fontsize=12, fontweight="bold")
    ax.set_ylabel("Execution Time (seconds)", fontsize=12, fontweight="bold")

    title = "Quantum Circuit Execution Time Scaling (per Replacement Probability)"
    if max_bond_dim:
        title += f", D={max_bond_dim}"

    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.legend(fontsize=10, loc="best")
    ax.grid(True, alpha=0.3)
    ax.set_yscale("log")

    fig.tight_layout()

    # Save if output path provided
    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig


def plot_execution_and_fidelity(
    results_dir: str | Path, repl_prob: float = None, output_path: str | Path = None
) -> plt.Figure:
    """
    Create a dual-subplot figure showing execution time (top) and fidelity (bottom) vs qubits.

    Parameters
    ----------
    results_dir : str or Path
        Path to the results directory containing benchmark results.
    repl_prob : float, optional
        Replacement probability to plot. If None, uses the first available.
    output_path : str or Path, optional
        If provided, save the figure to this path.

    Returns
    -------
    plt.Figure
        The matplotlib figure object with two subplots.
    """
    # Parse results with fidelities
    raw_data = parse_results_with_fidelity(results_dir)

    if not raw_data:
        raise ValueError(f"No results found in {results_dir}")

    # Determine which replacement probability to use
    available_repl_probs = get_repl_probs(raw_data)
    if repl_prob is None:
        repl_prob = available_repl_probs[0]
    elif repl_prob not in available_repl_probs:
        raise ValueError(
            f"Replacement probability {repl_prob} not found. Available: {available_repl_probs}"
        )

    # Filter and clean engine names (remove _sparse from mpstab)

    # all_engines = get_engines(raw_data)
    # cleaned_engines = filter_engines_for_plotting(all_engines)

    # Remap raw_data to use cleaned engine names
    remapped_data = defaultdict(lambda: defaultdict(dict))
    for engine_name, repl_dict in raw_data.items():
        if "mpstab" in engine_name and "_sparse" in engine_name:
            # Remove _sparse from mpstab engines
            cleaned_name = engine_name.replace("_sparse", "")
        else:
            cleaned_name = engine_name

        for repl_prob_val, qubit_dict in repl_dict.items():
            remapped_data[cleaned_name][repl_prob_val] = qubit_dict

    # Filter data to a single replacement probability
    filtered_data = defaultdict(lambda: defaultdict(dict))
    for engine_name, repl_dict in remapped_data.items():
        if repl_prob in repl_dict:
            filtered_data[engine_name][repl_prob] = repl_dict[repl_prob]

    if not dict(filtered_data):
        raise ValueError(f"No data found for replacement probability {repl_prob}")

    # Get color map for engines (using cleaned names)
    color_map = get_engine_color_map(list(filtered_data.keys()))

    # Create figure with two subplots sharing x-axis
    fig, (ax_time, ax_fidelity) = plt.subplots(2, 1, figsize=(12, 9), sharex=True)

    # Track fidelity range to set appropriate axis limits
    fidelity_values = []

    # Plot execution times and fidelities for each engine
    for engine_name in sorted(filtered_data.keys()):
        qubit_data = filtered_data[engine_name][repl_prob]
        qubits = sorted(qubit_data.keys())

        # Extract data
        exec_times = []
        exec_sems = []
        fidelities = []
        fidelity_mads = []

        for n in qubits:
            entry = qubit_data[n]

            # Execution time statistics
            times = np.array(entry["execution_times"])
            exec_times.append(np.mean(times))
            exec_sems.append(np.std(times) / np.sqrt(len(times)))

            # Fidelity statistics
            fids = np.array(entry["fidelities"])
            fidelities.append(np.mean(fids))
            fidelity_values.extend(fids.tolist())  # Track all fidelity values
            # Use MAD as uncertainty estimate
            fidelity_mads.append(np.median(np.abs(fids - np.median(fids))))

        # Get styling
        style = color_map[engine_name]
        bond_dim = extract_bond_dimension(engine_name)
        marker = get_marker_for_simulator(style["simulator"])

        # Create label with bond dimension if applicable
        if bond_dim is not None:
            label = f"{style['simulator']} D={bond_dim} ({style['matrix_type']})"
        else:
            label = f"{style['simulator']} ({style['matrix_type']})"

        # Plot execution time
        ax_time.errorbar(
            qubits,
            exec_times,
            yerr=exec_sems,
            marker=marker,
            linestyle="-",
            linewidth=2.5,
            label=label,
            color=style["color"],
            capsize=5,
            capthick=2,
            markersize=8,
            markeredgecolor="black",
            markeredgewidth=1.5,
            alpha=0.7,
            ecolor="black",
        )

        # Plot fidelity
        ax_fidelity.errorbar(
            qubits,
            fidelities,
            yerr=fidelity_mads,
            marker=marker,
            linestyle="-",
            linewidth=2.5,
            label=label,
            color=style["color"],
            capsize=5,
            capthick=2,
            markersize=8,
            markeredgecolor="black",
            markeredgewidth=1.5,
            alpha=0.7,
            ecolor="black",
        )

    # Format execution time subplot (top)
    ax_time.set_ylabel("Execution Time (seconds)", fontsize=12, fontweight="bold")
    ax_time.set_yscale("log")
    ax_time.grid(True, alpha=0.3, which="both")
    ax_time.legend(fontsize=11, loc="upper left")

    title = f"Quantum Circuit Benchmarking (p={repl_prob})"
    ax_time.set_title(title, fontsize=14, fontweight="bold", pad=15)

    # Format fidelity subplot (bottom)
    ax_fidelity.set_xlabel("Number of Qubits", fontsize=12, fontweight="bold")
    ax_fidelity.set_ylabel("Fidelity", fontsize=12, fontweight="bold")

    # Dynamically set y-axis limits based on data
    if fidelity_values:
        fid_min = min(fidelity_values)
        fid_max = max(fidelity_values)
        fid_range = fid_max - fid_min

        # If all fidelities are exactly 1.0, show a small range around it
        if fid_range < 1e-10:
            ax_fidelity.set_ylim([0.99, 1.001])
        else:
            # Add 10% padding
            padding = fid_range * 0.1
            ax_fidelity.set_ylim([fid_min - padding, fid_max + padding])
    else:
        ax_fidelity.set_ylim([0.95, 1.01])

    ax_fidelity.grid(True, alpha=0.3)
    ax_fidelity.legend(fontsize=11, loc="lower left")

    fig.tight_layout()

    # Save if output path provided
    if output_path:
        fig.savefig(output_path, dpi=300, bbox_inches="tight")

    return fig
