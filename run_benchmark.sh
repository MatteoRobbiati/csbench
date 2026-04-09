#!/bin/bash

# Bash script template for running quantum circuit benchmarks

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="${SCRIPT_DIR}/main.py"

# Common parameters
ANSATZ="hardware_efficient"
OBSERVABLE="central_x"
QUBIT_COUNTS=(3 5 7 9 11 13 15 17 19 21 23 25 27)
DEPTH=4
N_CIRCUITS=5
RNG_SEED=42
MAGIC_REPLACEMENT_PROB=0.85
RESULTS_DIR="${SCRIPT_DIR}/results"
DEVICE_TYPE="cpu"
MACHINE_PRECISION="float64"

# Function to run a single benchmark
run_benchmark() {
    local engine=$1
    local nqubits=$2
    local num_threads=$3
    local backend=$4
    local platform=$5
    local sim_kwargs=$6
    local use_sparse=$7
    
    echo "=========================================="
    echo "Running Quantum Circuit Benchmark"
    echo "=========================================="
    echo "Engine:                 $engine"
    if [ "$engine" = "statevector" ]; then
        echo "StateVector Backend:    $backend"
        if [ ! -z "$platform" ]; then
            echo "StateVector Platform:   $platform"
        fi
    fi
    if [ ! -z "$sim_kwargs" ]; then
        echo "Simulation Kwargs:      $sim_kwargs"
    fi
    echo "Num Threads:            $num_threads"
    echo "Use Sparse:             $use_sparse"
    echo "Device Type:            $DEVICE_TYPE"
    echo "Machine Precision:      $MACHINE_PRECISION"
    echo "Ansatz:                 $ANSATZ"
    echo "Observable:             $OBSERVABLE"
    echo "Qubits:                 $nqubits"
    echo "Depth:                  $DEPTH"
    echo "Number of Circuits:     $N_CIRCUITS"
    echo "RNG Seed:               $RNG_SEED"
    echo "Magic Replacement Prob: $MAGIC_REPLACEMENT_PROB"
    echo "Results Directory:      $RESULTS_DIR"
    echo "=========================================="
    echo ""

    python "$PYTHON_SCRIPT" \
        --engine "$engine" \
        --ansatz "$ANSATZ" \
        --observable "$OBSERVABLE" \
        --nqubits "$nqubits" \
        --depth "$DEPTH" \
        --n-circuits "$N_CIRCUITS" \
        --rng-seed "$RNG_SEED" \
        --magic-replacement-prob "$MAGIC_REPLACEMENT_PROB" \
        --results-dir "$RESULTS_DIR" \
        --statevector-backend "$backend" \
        --statevector-platform "$platform" \
        --simulation-kwargs "$sim_kwargs" \
        --num-threads "$num_threads" \
        --device-type "$DEVICE_TYPE" \
        --machine-precision "$MACHINE_PRECISION" \
        --sparse "$use_sparse"

    if [ $? -eq 0 ]; then
        echo ""
        echo "=========================================="
        echo "Benchmark ($engine, $nqubits qubits) completed successfully!"
        echo "=========================================="
        echo ""
    else
        echo ""
        echo "=========================================="
        echo "Benchmark ($engine, $nqubits qubits) failed!"
        echo "=========================================="
        exit 1
    fi
}

# Main loop over qubit counts
for nqubits in "${QUBIT_COUNTS[@]}"; do
    echo ""
    echo "###########################################################"
    echo "# Running benchmarks for $nqubits qubits"
    echo "###########################################################"
    echo ""

    # Run 1: qibojit single thread with sparse matrices
    echo "###########################################################"
    echo "# Run 1: StateVector (qibojit) - Single Thread - Sparse"
    echo "###########################################################"
    echo ""
    run_benchmark "statevector" "$nqubits" "1" "qibojit" "" "" "true"

    # Run 2: mpstab with bond dimension 32 with sparse matrices
    echo "###########################################################"
    echo "# Run 2: MPS (mpstab) - Bond Dimension 32 - Sparse"
    echo "###########################################################"
    echo ""
    run_benchmark "mpstab" "$nqubits" "8" "" "" "max_bond_dimension=32" "true"

done

echo ""
echo "=========================================="
echo "All benchmarks completed successfully!"
echo "=========================================="
