#!/usr/bin/env python
"""Script for plotting quantum circuit benchmark results."""

import sys
from pathlib import Path

# Add src to path so we can import csbench
sys.path.insert(0, str(Path(__file__).parent / "src"))

import matplotlib.pyplot as plt

from csbench.ui.plot_scalings import (
    parse_results_with_fidelity,
    get_repl_probs,
    plot_execution_and_fidelity,
)


def main():
    """Generate benchmark plot with execution time and fidelity."""
    results_dir = Path("results")

    if not results_dir.exists():
        print(f"Results directory {results_dir} not found!")
        return

    # Parse available data
    raw_data = parse_results_with_fidelity(results_dir)
    available_repl_probs = get_repl_probs(raw_data)

    if not available_repl_probs:
        print("No data found!")
        return

    print(f"Available replacement probabilities: {available_repl_probs}")

    # Use the first available replacement probability
    repl_prob = available_repl_probs[1]
    print(f"\nGenerating plot for p={repl_prob}")

    # Create the dual-subplot figure
    _ = plot_execution_and_fidelity(
        results_dir,
        repl_prob=repl_prob,
        output_path=f"execution_and_fidelity_p{repl_prob:.2f}.png",
    )

    plt.show()


if __name__ == "__main__":
    main()
