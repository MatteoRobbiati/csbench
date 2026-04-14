#!/bin/bash
#SBATCH --job-name=mpstab_layers
#SBATCH --chdir=/home/mattiaro/csbench
#SBATCH --output=/home/mattiaro/csbench/logs/bench_TN_%A_%a.out
#SBATCH --error=/home/mattiaro/csbench/logs/benchTN_%A_%a.err
#SBATCH --array=0-20  
#SBATCH --cpus-per-task=8                                                   
#SBATCH --mem=32G
#SBATCH --time=04:00:00

# Thread configuration
NUM_THREADS=8 

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

# Simulation Parameters (Modificali liberamente, senza usare virgole)
QUBITS=(35)
LAYERS=(25 30)
BOND_DIMS=(8)
PROBS=(0.05 0.25 0.5 0.75 0.95)

# Calcolo dinamico delle dimensioni degli array
NUM_Q=${#QUBITS[@]}
NUM_L=${#LAYERS[@]}
NUM_B=${#BOND_DIMS[@]}
NUM_P=${#PROBS[@]}

# Safety check: verifica se ci sono abbastanza combinazioni
TOTAL_COMBINATIONS=$((NUM_Q * NUM_L * NUM_B * NUM_P))
if [ "$SLURM_ARRAY_TASK_ID" -ge "$TOTAL_COMBINATIONS" ]; then
    echo "Errore: SLURM_ARRAY_TASK_ID ($SLURM_ARRAY_TASK_ID) eccede il numero totale di combinazioni calcolate ($TOTAL_COMBINATIONS)."
    exit 1
fi

# Logic for Slurm Array Indexing (Dinamica)
ID=$SLURM_ARRAY_TASK_ID

p_idx=$(( ID % NUM_P ))
b_idx=$(( (ID / NUM_P) % NUM_B ))
l_idx=$(( (ID / (NUM_P * NUM_B)) % NUM_L ))
q_idx=$(( (ID / (NUM_P * NUM_B * NUM_L)) % NUM_Q ))

N_QUBITS=${QUBITS[$q_idx]}
N_LAYERS=${LAYERS[$l_idx]}
MAX_BOND=${BOND_DIMS[$b_idx]}
R_PROB=${PROBS[$p_idx]}

# Export variables for numerical libraries
export OMP_NUM_THREADS=$NUM_THREADS
export MKL_NUM_THREADS=$NUM_THREADS
export OPENBLAS_NUM_THREADS=$NUM_THREADS

echo "Running Configuration: Engine=TensorNetwork, Q=$N_QUBITS, L=$N_LAYERS, Bond=$MAX_BOND, Prob=$R_PROB"

# Execution
python "$PYTHON_SCRIPT" \
    --engine "tensor_network" \
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