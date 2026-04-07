#!/bin/bash

# Bash script template for running quantum circuit benchmarks

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/main.py"

# Default parameters
ENGINE="statevector"
ANSATZ="hardware_efficient"
OBSERVABLE="global_z"
NQUBITS=12
DEPTH=4
N_CIRCUITS=10
RNG_SEED=42
MAGIC_REPLACEMENT_PROB=0.8
RESULTS_DIR="${SCRIPT_DIR}/results"
STATEVECTOR_BACKEND="qibojit"
STATEVECTOR_PLATFORM="numba"

# Simulation kwargs (for mpstab engine: max_bond_dim, precision, etc.)
# Format: "key=value,key=value,..." or JSON format
# Examples:
# SIMULATION_KWARGS="max_bond_dimension=256,precision=64"
# SIMULATION_KWARGS='{"max_bond_dim": 256, "precision": 64}'
# SIMULATION_KWARGS="max_bond_dimension=256"

# Machine configuration
NUM_THREADS=8
DEVICE_TYPE="cpu"  # Options: cpu, gpu, cuda, tpu
MACHINE_PRECISION="float64"  # Options: float32, float64

# Print configuration
echo "=========================================="
echo "Quantum Circuit Benchmark Execution"
echo "=========================================="
echo "Engine:                 $ENGINE"
if [ "$ENGINE" = "statevector" ]; then
    echo "StateVector Backend:    $STATEVECTOR_BACKEND"
    echo "StateVector Platform:   $STATEVECTOR_PLATFORM"
fi
if [ ! -z "$SIMULATION_KWARGS" ]; then
    echo "Simulation Kwargs:      $SIMULATION_KWARGS"
fi
echo "Num Threads:            $NUM_THREADS"
echo "Device Type:            $DEVICE_TYPE"
echo "Machine Precision:      $MACHINE_PRECISION"
echo "Ansatz:                 $ANSATZ"
echo "Observable:             $OBSERVABLE"
echo "Qubits:                 $NQUBITS"
echo "Depth:                  $DEPTH"
echo "Number of Circuits:     $N_CIRCUITS"
echo "RNG Seed:               $RNG_SEED"
echo "Magic Replacement Prob: $MAGIC_REPLACEMENT_PROB"
echo "Results Directory:      $RESULTS_DIR"
echo "=========================================="
echo ""

# Run benchmark
python "$PYTHON_SCRIPT" \
    --engine "$ENGINE" \
    --ansatz "$ANSATZ" \
    --observable "$OBSERVABLE" \
    --nqubits "$NQUBITS" \
    --depth "$DEPTH" \
    --n-circuits "$N_CIRCUITS" \
    --rng-seed "$RNG_SEED" \
    --magic-replacement-prob "$MAGIC_REPLACEMENT_PROB" \
    --results-dir "$RESULTS_DIR" \
    --statevector-backend "$STATEVECTOR_BACKEND" \
    --statevector-platform "$STATEVECTOR_PLATFORM" \
    --simulation-kwargs "$SIMULATION_KWARGS" \
    --num-threads "$NUM_THREADS" \
    --device-type "$DEVICE_TYPE" \
    --machine-precision "$MACHINE_PRECISION"

# Check execution status
if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "Benchmark completed successfully!"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "Benchmark failed!"
    echo "=========================================="
    exit 1
fi
