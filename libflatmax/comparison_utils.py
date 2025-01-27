import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from oct2py import octave
from itertools import zip_longest

def generate_test_input(plotting=False, random_data=False):
    if random_data:
        df = pd.DataFrame(np.cumsum(np.random.rand(1024)), columns=['price'])
    else:
        df = pd.read_csv("./data/btc_last_3_days_kraken.csv", 
                       parse_dates=['time'], index_col='time')
    return df

def plot_comparison(signal, oct_min_idx, oct_mins, oct_max_idx, oct_maxs,
                   oct_up, oct_down, py_min_idx, py_mins, py_max_idx, py_maxs,
                   py_up, py_down):
    plt.clf()
    plt.plot(signal, label="Signal", color="blue")
    
    # Octave results
    plt.plot(oct_min_idx, oct_mins, 'go', label="Octave Min")
    plt.plot(oct_up, signal[oct_up], 'g*', label="Octave Up")
    plt.plot(oct_max_idx, oct_maxs, 'ro', label="Octave Max")
    plt.plot(oct_down, signal[oct_down], 'r*', label="Octave Down")
    
    # Python results
    plt.plot(py_min_idx, py_mins, 'bx', label="Python Min")
    plt.plot(py_up, signal[py_up], 'b+', label="Python Up")
    plt.plot(py_max_idx, py_maxs, 'mx', label="Python Max") 
    plt.plot(py_down, signal[py_down], 'm+', label="Python Down")
    
    plt.grid(True)
    plt.legend()
    plt.show()

def compare_results(oct_vec, py_vec, name):
    if len(oct_vec) != len(py_vec):
        print(f"{name} LENGTH MISMATCH: Octave {len(oct_vec)} vs Python {len(py_vec)}")
        return False
    
    match = np.allclose(oct_vec, py_vec, atol=1e-6, equal_nan=True)
    if not match:
        print(f"{name} VALUE MISMATCHES:")
        for i, (o, p) in enumerate(zip(oct_vec, py_vec)):
            if not np.isclose(o, p, atol=1e-6):
                print(f"Index {i}: Octave {o:.6f} vs Python {p:.6f}")
    return match

def print_compact_table(oct_arr, py_arr, title, fmt="%d"):
    print(f"\n{title} comparison:")
    print(f"{'Octave':<15} | {'Python':<15}")
    print("-"*32)
    for o, p in zip_longest(oct_arr, py_arr, fillvalue=np.nan):
        o = o[0] if isinstance(o, np.ndarray) else o
        p = p[0] if isinstance(p, np.ndarray) else p
        
        o_str = (fmt % o) if (np.isscalar(o) and not np.isnan(o)) else "N/A"
        p_str = (fmt % p) if (np.isscalar(p) and not np.isnan(p)) else "N/A"
        print(f"{o_str:<15} | {p_str:<15}")

def run_comparison_test(octave_fn, python_fn, signal, criterion, test_name):
    # Run Octave implementation
    oct_results = octave_fn(signal, criterion, nout=6)
    (min_indexes, max_indexes, maxs, mins, 
     up_breakpoints, down_breakpoints) = oct_results
     
    # Convert Octave indices to Python 0-based
    min_indexes = (min_indexes - 1).flatten().astype(int)
    max_indexes = (max_indexes - 1).flatten().astype(int)
    up_breakpoints = (np.array(up_breakpoints).flatten() - 1).astype(int)
    down_breakpoints = (np.array(down_breakpoints).flatten() - 1).astype(int)

    # Run Python implementation
    py_results = python_fn(signal, criterion)
    (py_min_idx, py_max_idx, py_maxs, py_mins, 
     py_up, py_down) = py_results

    # Compare results
    print(f"\n=== {test_name} Results Comparison ===")
    all_match = True
    for name, oct_data, py_data in [
        ("Min indexes", min_indexes, py_min_idx),
        ("Max indexes", max_indexes, py_max_idx),
        ("Mins values", mins.flatten(), py_mins),
        ("Maxs values", maxs.flatten(), py_maxs),
        ("Up breakpoints", up_breakpoints, py_up),
        ("Down breakpoints", down_breakpoints, py_down)
    ]:
        print(f"\n{name}:")
        oct_clean = np.array(oct_data).astype(float)
        py_clean = np.array(py_data).astype(float)
        print("Octave:", np.array_repr(oct_clean).replace('\n', '')[:70], "...")
        print("Python:", np.array_repr(py_clean).replace('\n', '')[:70], "...")
        all_match &= compare_results(oct_clean, py_clean, name)

    print("\n=== Final Result ===")
    print("ALL OUTPUTS MATCH:", "YES" if all_match else "NO")

    # Print compact tables
    print("\n=== Compact Comparison Table ===")
    print_compact_table(min_indexes, py_min_idx, "Min Indexes")
    print_compact_table(max_indexes, py_max_idx, "Max Indexes", fmt="%d")
    print_compact_table(up_breakpoints, py_up, "Up Breakpoints", fmt="%d")
    print_compact_table(down_breakpoints, py_down, "Down Breakpoints", fmt="%d")

    # Plot comparison
    plot_comparison(signal, 
                   min_indexes, mins.flatten(), 
                   max_indexes, maxs.flatten(),
                   up_breakpoints, down_breakpoints,
                   py_min_idx, py_mins, 
                   py_max_idx, py_maxs,
                   py_up, py_down)
    return all_match
