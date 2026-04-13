#!/bin/bash
#SBATCH --job-name=csbench
#SBATCH --chdir=/home/mattiaro/csbench
#SBATCH --output=/home/mattiaro/csbench/logs/bench_MPSTAB_%A_%a.out
#SBATCH --error=/home/mattiaro/csbench/logs/benchMPSTAB_%A_%a.err
#SBATCH --array=0-209                                                       # 210 parameter combinations
#SBATCH --cpus-per-task=1                                                   # Set this to the maximum threads you might ever use
#SBATCH --mem=32G

# Set your desired number of threads here
NUM_THREADS=1 

# Module Loading
module purge
module load Python/3.12.3-GCCcore-13.3.0
source ~/envs/mpstab/bin/activate

# Directories and Setup
PROJECT_DIR="/home/mattiaro/csbench"
PYTHON_SCRIPT="${PROJECT_DIR}/main.py"
RESULTS_DIR="${PROJECT_DIR}/results"
LOGS_DIR="${PROJECT_DIR}/logs"
mkdir -p "$RESULTS_DIR" "$LOGS_DIR"

# Simulation Parameters
QUBITS=(3 13 23 33 43 53 63)
LAYERS=(1 5)
BOND_DIMS=(2 8 32)
PROBS=(0.05 0.25 0.5 0.75 0.95)

# Logic for Slurm Array Indexing (0-209)
ID=$SLURM_ARRAY_TASK_ID
p_idx=$(( ID % 5 ))
b_idx=$(( (ID / 5) % 3 ))
l_idx=$(( (ID / 15) % 2 ))
q_idx=$(( (ID / 30) % 7 ))

N_QUBITS=${QUBITS[$q_idx]}
N_LAYERS=${LAYERS[$l_idx]}
MAX_BOND=${BOND_DIMS[$b_idx]}
R_PROB=${PROBS[$p_idx]}

# Dynamic Resource Configuration
# This creates the mask string "0-0", "0-7", "0-15", etc. based on NUM_THREADS
# CORE_MASK="0-$(( NUM_THREADS - 1 ))"

# Export variables for numerical libraries (OpenMP, MKL)
export OMP_NUM_THREADS=$NUM_THREADS
export MKL_NUM_THREADS=$NUM_THREADS
export OPENBLAS_NUM_THREADS=$NUM_THREADS

echo "Running Configuration: Q=$N_QUBITS, L=$N_LAYERS, Bond=$MAX_BOND, Prob=$R_PROB"
echo "Execution Resources: $NUM_THREADS thread(s) restricted to core mask: $CORE_MASK"

# Execution with taskset and dynamic variables
taskset -c "$CORE_MASK" python "$PYTHON_SCRIPT" \
    --engine "mpstab" \
    --ansatz "hardware_efficient" \
    --observable "central_x" \
    --nqubits "$N_QUBITS" \
    --depth "$N_LAYERS" \
    --n-circuits 5 \
    --rng-seed 42 \
    --magic-replacement-prob "$R_PROB" \
    --results-dir "$RESULTS_DIR" \
    --simulation-kwargs "max_bond_dimension=$MAX_BOND" \
    --num-threads "$NUM_THREADS" \
    --device-type "cpu" \
    --machine-precision "float64" \
    --sparse "true"
