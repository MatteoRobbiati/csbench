#!/usr/bin/env python
"""Main script for running quantum circuit benchmarks."""

import click
from csbench.execute import run_benchmark
from csbench.utils import parse_simulation_kwargs


@click.command()
@click.option(
    "--engine",
    type=click.Choice(["statevector", "mpstab"]),
    default="statevector",
    help="Benchmark engine to use"
)
@click.option(
    "--ansatz",
    type=str,
    default="hardware_efficient",
    help="Circuit ansatz to use"
)
@click.option(
    "--observable",
    type=click.Choice(["central_x", "global_z"]),
    default="global_z",
    help="Observable to measure"
)
@click.option(
    "--nqubits",
    type=int,
    default=4,
    help="Number of qubits"
)
@click.option(
    "--depth",
    type=int,
    default=2,
    help="Circuit depth"
)
@click.option(
    "--n-circuits",
    type=int,
    default=10,
    help="Number of circuit variations to generate"
)
@click.option(
    "--rng-seed",
    type=int,
    default=42,
    help="Random seed for reproducibility"
)
@click.option(
    "--magic-replacement-prob",
    type=float,
    default=0.1,
    help="Magic gate replacement probability"
)
@click.option(
    "--results-dir",
    type=str,
    default="results",
    help="Base results directory"
)
@click.option(
    "--statevector-backend",
    type=str,
    default="numpy",
    help="Backend for StateVector engine (e.g., numpy, qibojit-numba, qibojit-jax)"
)
@click.option(
    "--statevector-platform",
    type=str,
    default=None,
    help="Platform for StateVector engine (optional)"
)
@click.option(
    "--simulation-kwargs",
    type=str,
    default=None,
    help="Simulation configuration as JSON (e.g., '{\"max_bond_dimension\": 256}') or key=value pairs separated by commas (e.g., 'max_bond_dimension=256,precision=64')"
)
@click.option(
    "--num-threads",
    type=int,
    default=1,
    help="Number of CPU threads to use"
)
@click.option(
    "--device-type",
    type=click.Choice(["cpu", "gpu", "cuda", "tpu"]),
    default="cpu",
    help="Device type for computation"
)
@click.option(
    "--machine-precision",
    type=click.Choice(["float32", "float64"]),
    default="float64",
    help="Numerical precision for computation"
)
def main(engine, ansatz, observable, nqubits, depth, n_circuits, rng_seed, 
         magic_replacement_prob, results_dir, statevector_backend, statevector_platform, 
         simulation_kwargs, num_threads, device_type, machine_precision):
    """Run quantum circuit benchmarks."""
    
    # Parse simulation kwargs
    sim_kwargs = parse_simulation_kwargs(simulation_kwargs)
    
    # Build engine kwargs
    engine_kwargs = {}
    if engine == "statevector":
        engine_kwargs["_qibo_backend_name"] = statevector_backend
        engine_kwargs["_qibo_platform_name"] = statevector_platform
    
    # Add simulation kwargs to engine kwargs for mpstab
    if engine == "mpstab":
        engine_kwargs.update(sim_kwargs)
    
    # Run benchmark
    result = run_benchmark(
        engine_name=engine,
        ansatz_name=ansatz,
        nqubits=nqubits,
        depth=depth,
        n_circuits=n_circuits,
        rng_seed=rng_seed,
        magic_replacement_prob=magic_replacement_prob,
        observable_name=observable,
        base_results_dir=results_dir,
        simulation_kwargs=sim_kwargs,
        num_threads=num_threads,
        device_type=device_type,
        precision=machine_precision,
        **engine_kwargs
    )
    
    click.echo(f"Results saved to: {result['results_path']}")
    click.echo("Files created:")
    for key, path in result['saved_files'].items():
        click.echo(f"  {key}: {path}")
    click.echo(f"\nExecutions: {result['num_executions']}")
    click.echo()
    click.echo("=" * 50)
    click.echo("Benchmark completed successfully!")
    click.echo("=" * 50)


if __name__ == "__main__":
    main()
