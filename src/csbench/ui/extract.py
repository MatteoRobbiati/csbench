import json
import re
import pandas as pd
from pathlib import Path

def extract_simulation_results(base_directory):
    data_list = []
    base_path = Path(base_directory)

    # Patterns for the two folder levels
    param_folder_pattern = re.compile(r"qubits(\d+)_layers(\d+)_repl_prob([\d\.]+)_seed(\d+)")
    engine_folder_pattern = re.compile(r"(mpstab|tensor_network)_sparse_max_bond_dimension(\d+)")

    # 1. Iterate through parameter folders (qubits...)
    for param_folder in base_path.iterdir():
        if not param_folder.is_dir():
            continue
            
        param_match = param_folder_pattern.search(param_folder.name)
        if not param_match:
            continue

        qubits = int(param_match.group(1))
        layers = int(param_match.group(2))
        repl_prob = float(param_match.group(3))
        seed = int(param_match.group(4))

        # 2. Iterate through engine subfolders (mpstab...)
        for engine_folder in param_folder.iterdir():
            if not engine_folder.is_dir():
                continue
                
            engine_match = engine_folder_pattern.search(engine_folder.name)
            if not engine_match:
                continue

            engine = engine_match.group(1)
            max_bond_dim = int(engine_match.group(2))

            # 3. Find and read all JSON files inside the engine folder
            for json_file in engine_folder.glob("*.json"):
                try:
                    with open(json_file, 'r') as f:
                        content = json.load(f)
                    
                    stats = content.get("statistics", {})

                    record = {
                        "qubits": qubits,
                        "layers": layers,
                        "repl_prob": repl_prob,
                        "seed": seed,
                        "engine": engine,
                        "max_bond_dimension": max_bond_dim,
                        "filename": json_file.name,
                        "expectation_value_median": stats.get("expectation_value", {}).get("median"),
                        "expectation_value_mad": stats.get("expectation_value", {}).get("mad"),
                        "execution_time_median": stats.get("execution_time", {}).get("median"),
                        "execution_time_mad": stats.get("execution_time", {}).get("mad"),
                        "fidelity_median": stats.get("fidelity", {}).get("median"),
                        "fidelity_mad": stats.get("fidelity", {}).get("mad")
                    }
                    data_list.append(record)
                    
                except Exception as e:
                    print(f"Error reading {json_file}: {e}")

    return pd.DataFrame(data_list)

# --- Usage ---
path = "/home/mattiaro/csbench/results/hardware_efficient_central_x/"
results_df = extract_simulation_results(path)

if not results_df.empty:
    print(f"Successfully extracted {len(results_df)} records.")
    results_df.to_csv("simulation_results.csv", index=False)
else:
    print("No data found. Check your folder patterns.")