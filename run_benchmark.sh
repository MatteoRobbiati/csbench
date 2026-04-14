#!/bin/bash
<<<<<<< HEAD
#SBATCH --job-name=csbench_tn
#SBATCH --chdir=/home/mattiaro/csbench
#SBATCH --output=/home/mattiaro/csbench/logs/bench_TN_%A_%a.out
#SBATCH --error=/home/mattiaro/csbench/logs/benchTN_%A_%a.err
#SBATCH --array=0-989                                                       # 990 combinazioni totali
#SBATCH --cpus-per-task=1                                                   
#SBATCH --mem=32G
#SBATCH --time=01:00:00                                                     # Aumentato il tempo per circuiti più profondi/bond dim elevate

# Thread configuration
=======
#SBATCH --job-name=csbench
#SBATCH --chdir=/home/mattiaro/csbench
#SBATCH --output=/home/mattiaro/csbench/logs/bench_MPSTAB_%A_%a.out
#SBATCH --error=/home/mattiaro/csbench/logs/benchMPSTAB_%A_%a.err
#SBATCH --array=0-209                                                       # 210 parameter combinations
#SBATCH --cpus-per-task=1                                                   # Set this to the maximum threads you might ever use
#SBATCH --mem=32G

# Set your desired number of threads here
>>>>>>> 3446391e6b9bf95636f68fbf72ccddabd86d8e38
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
<<<<<<< HEAD
QUBITS=(5 15 25 35 45 55 65 75 85 95 105)        # 11 valori
LAYERS=(1 5 10)                                 # 3 valori
BOND_DIMS=(2 4 8 16 32 64)                      # 6 valori
PROBS=(0.05 0.25 0.5 0.75 0.95)                 # 5 valori

# Logic for Slurm Array Indexing (Mappatura 990 combinazioni)
ID=$SLURM_ARRAY_TASK_ID

p_idx=$(( ID % 5 ))                             # Cicla ogni 5 (Probs)
b_idx=$(( (ID / 5) % 6 ))                       # Cicla ogni 30 (Bond Dims)
l_idx=$(( (ID / 30) % 3 ))                      # Cicla ogni 90 (Layers)
q_idx=$(( (ID / 90) % 11 ))                     # Cicla ogni 990 (Qubits)

N_QUBITS=${QUBITS[$q_idx]}
N_LAYERS=${LAYERS[$l_idx]}
MAX_BOND=${BOND_DIMS[$b_idx]}
R_PROB=${PROBS[$p_idx]}

# Export variables for numerical libraries
=======
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
>>>>>>> 3446391e6b9bf95636f68fbf72ccddabd86d8e38
export OMP_NUM_THREADS=$NUM_THREADS
export MKL_NUM_THREADS=$NUM_THREADS
export OPENBLAS_NUM_THREADS=$NUM_THREADS

<<<<<<< HEAD
echo "Running Configuration: Engine=TensorNetwork, Q=$N_QUBITS, L=$N_LAYERS, Bond=$MAX_BOND, Prob=$R_PROB"

# Execution
python "$PYTHON_SCRIPT" \
    --engine "tensor_network" \
=======
echo "Running Configuration: Q=$N_QUBITS, L=$N_LAYERS, Bond=$MAX_BOND, Prob=$R_PROB"
echo "Execution Resources: $NUM_THREADS thread(s) restricted to core mask: $CORE_MASK"

# Execution with taskset and dynamic variables
taskset -c "$CORE_MASK" python "$PYTHON_SCRIPT" \
    --engine "mpstab" \
>>>>>>> 3446391e6b9bf95636f68fbf72ccddabd86d8e38
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
<<<<<<< HEAD
    --sparse "true"
=======
    --sparse "true"
>>>>>>> 3446391e6b9bf95636f68fbf72ccddabd86d8e38
