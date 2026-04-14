import os
import psutil
import platform

from csbench.engines.abstract import BenchmarkEngine


def configure_environment(
    simulation_engine: BenchmarkEngine,
    num_threads: int = 1,
    device_type: str = "cpu",
    precision: str = "float64",
) -> str:
    """
    Configures the simulation environment including threading, hardware affinity, device, and precision.

    This function should be called at the beginning of benchmark execution to ensure
    proper resource allocation and numerical precision.

    Args:
        simulation_engine (BenchmarkEngine): The benchmark engine instance to configure
        num_threads (int): Number of CPU threads to allow (default: 1)
        device_type (str): Device to use - 'cpu', 'gpu', 'cuda', or 'tpu' (default: 'cpu')
        precision (str): Numerical precision - 'float32' or 'float64' (default: 'float64')

    Returns:
        str: The configured device type
    """

    # 1. SET THREADING ENVIRONMENT VARIABLES (Library Level)
    # This covers OpenMP, MKL, and OpenBLAS
    t_str = str(num_threads)
    for var in [
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
    ]:
        os.environ[var] = t_str
    print(f"Set {t_str} threads for: OMP, MKL, OpenBLAS, VecLib")

    # 2. SET HARDWARE AFFINITY (OS Level)
    # Only works on Linux/Windows; skips on macOS
    if platform.system() != "Darwin":
        try:
            # In un ambiente Slurm, il processo è già limitato ai core corretti.
            # Forzare range(num_threads) potrebbe causare errori di permessi.
            affinity = os.sched_getaffinity(0)
            print(f"Slurm/OS allocated cores: {affinity}")
        except Exception as e:
            print(f"Warning: Could not check CPU affinity: {e}")
    else:
        print("macOS detected: Skipping affinity check.")
    # 3. SET ENGINE DEVICE AND PRECISION
    # Normalize device name
    target_device = _normalize_device(device_type)

    # Set machine parameters on the engine
    simulation_engine.set_machine_parameters(device=target_device, precision=precision)

    # 4. FOR STATEVECTOR ENGINE: SET QIBO BACKEND DEVICE AND PRECISION
    if (
        hasattr(simulation_engine, "qibo_backend")
        and simulation_engine.qibo_backend is not None
    ):
        try:
            # Using Qibo notation
            if target_device == "cpu":
                qibo_target_device = "/CPU:0"
            elif target_device == "gpu":
                qibo_target_device = "/GPU:0"

            # Qibo backends support set_device, set_precision and set_threads
            if hasattr(simulation_engine.qibo_backend, "set_device"):
                simulation_engine.qibo_backend.set_device(qibo_target_device)
                simulation_engine.qibo_backend.set_threads(num_threads)
            if hasattr(simulation_engine.qibo_backend, "set_precision"):
                simulation_engine.qibo_backend.set_precision(precision)
            print(
                f"Qibo backend configured: device={target_device}, precision={precision}, threads: {num_threads}"
            )
        except Exception as e:
            print(f"Warning: Could not configure Qibo backend device/precision: {e}")

    print(
        f"--- Configuration Complete: Threads={num_threads}, Device={target_device}, Precision={precision} ---"
    )
    return target_device


def _normalize_device(device_type: str) -> str:
    """
    Normalize device type strings to standard format.

    Args:
        device_type (str): Raw device type input

    Returns:
        str: Normalized device type
    """
    mapping = {
        "gpu": "cuda",
        "cuda": "cuda",
        "tpu": "tpu",
        "cpu": "cpu",
    }
    normalized = mapping.get(device_type.lower(), "cpu")

    # Special case for macOS
    if platform.system() == "Darwin" and device_type.lower() == "gpu":
        print(
            "Warning: macOS detected. Metal Performance Shaders (MPS) not directly set here."
        )
        normalized = "cpu"

    return normalized


# Example Usage:
# from csbench.engines.statevector import StateVectorEngine
# engine = StateVectorEngine()
# configure_environment(engine, num_threads=4, device_type='cpu', precision='float64')
