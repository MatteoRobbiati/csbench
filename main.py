#!/usr/bin/env python
"""Main script for running quantum circuit benchmarks."""

import argparse

from csbench.execute import run_benchmark
from csbench.utils import parse_simulation_kwargs

def str2bool(v):
    """Convert string to boolean."""
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def main():
    """Run quantum circuit benchmarks."""
    parser = argparse.ArgumentParser(description="Run quantum circuit benchmarks.")

    parser.add_argument(
        "--engine",
        choices=["statevector", "mpstab", "tensor_network"],
        default="statevector",
        help="Benchmark engine to use",
    )
    parser.add_argument(
        "--ansatz",
        type=str,
        default="hardware_efficient",
        help="Circuit ansatz to use",
    )
    parser.add_argument(
        "--observable",
        choices=["central_x", "global_z"],
        default="global_z",
        help="Observable to measure",
    )
    parser.add_argument(
        "--nqubits",
        type=int,
        default=4,
        help="Number of qubits",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Circuit depth",
    )
    parser.add_argument(
        "--n-circuits",
        type=int,
        default=10,
        help="Number of circuit variations to generate",
    )
    parser.add_argument(
        "--rng-seed",
        type=int,
        default=42,
        help="Random seed for reproducibility",
    )
    parser.add_argument(
        "--magic-replacement-prob",
        type=float,
        default=0.1,
        help="Magic gate replacement probability",
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="results",
        help="Base results directory",
    )
    parser.add_argument(
        "--statevector-backend",
        type=str,
        default="numpy",
        help="Backend for StateVector engine (e.g., numpy, qibojit-numba, qibojit-jax)",
    )
    parser.add_argument(
        "--statevector-platform",
        type=str,
        default=None,
        help="Platform for StateVector engine (optional)",
    )
    parser.add_argument(
        "--simulation-kwargs",
        type=str,
        default=None,
        help="Simulation configuration as JSON (e.g., '{\"max_bond_dimension\": 256}') or key=value pairs separated by commas (e.g., 'max_bond_dimension=256,precision=64')",
    )
    parser.add_argument(
        "--num-threads",
        type=int,
        default=1,
        help="Number of CPU threads to use",
    )
    parser.add_argument(
        "--device-type",
        choices=["cpu", "gpu", "cuda", "tpu"],
        default="cpu",
        help="Device type for computation",
    )
    parser.add_argument(
        "--machine-precision",
        choices=["float32", "float64"],
        default="float64",
        help="Numerical precision for computation",
    )
    parser.add_argument(
        "--sparse",
        type=str2bool,
        default=True,
        help="Use sparse matrix representation for observables (default: True)",
    )

    args = parser.parse_args()

    # Parse simulation kwargs
    sim_kwargs = parse_simulation_kwargs(args.simulation_kwargs)

    # Build engine kwargs
    engine_kwargs = {}
    if args.engine == "statevector":
        engine_kwargs["_qibo_backend_name"] = args.statevector_backend
        engine_kwargs["_qibo_platform_name"] = args.statevector_platform

    # Add simulation kwargs to engine kwargs for mpstab
    if args.engine in ["mpstab", "tensor_network"]:
        engine_kwargs.update(sim_kwargs)

    # Run benchmark
    result = run_benchmark(
        engine_name=args.engine,
        ansatz_name=args.ansatz,
        nqubits=args.nqubits,
        depth=args.depth,
        n_circuits=args.n_circuits,
        rng_seed=args.rng_seed,
        magic_replacement_prob=args.magic_replacement_prob,
        observable_name=args.observable,
        base_results_dir=args.results_dir,
        simulation_kwargs=sim_kwargs,
        num_threads=args.num_threads,
        device_type=args.device_type,
        precision=args.machine_precision,
        use_sparse=args.sparse,
        **engine_kwargs,
    )

    print(f"Results saved to: {result['results_path']}")
    print("Files created:")
    for key, path in result["saved_files"].items():
        print(f"  {key}: {path}")
    print(f"\nExecutions: {result['num_executions']}")
    print()
    print("=" * 50)
    print("Benchmark completed successfully!")
    print("=" * 50)



if __name__ == "__main__":
    main()
