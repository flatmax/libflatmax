#!/usr/bin/env python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from libflatmax.findMaxsMins3 import find_maxs_mins3
from oct2py import octave

def generate_test_input(plotting = False, random_data = False):
    if random_data:
        df = pd.DataFrame(np.cumsum(np.random.rand(1024)), columns=['price'])
    else:
        # Load the CSV file
        # df = pd.read_csv("./data/btc_last_3_days.csv")
        # Load the CSV and parse dates
        # df = pd.read_csv("./data/btc_last_3_days.csv", parse_dates=['timestamp'], index_col='timestamp')
        df = pd.read_csv("./data/btc_last_3_days_kraken.csv", parse_dates=['time'], index_col='time')

    # print(df.head())

    if plotting:
        # Plot the data
        plt.figure(figsize=(10, 6))  # Optional: set figure size
        # plt.plot(df.index, df['price'], label='BTC Price')  # Replace 'price' with the actual column name if different
        plt.plot(df.index, df['close'], label='BTC Price')  # Replace 'price' with the actual column name if different
        plt.xlabel("Time")
        plt.ylabel("Price (USD)")
        plt.title("Bitcoin Price Over Last 3 Days")
        plt.legend()
        plt.grid(True)
        plt.show()

    return df


def plot_local(signal, oct_min_idx, oct_mins, oct_max_idx, oct_maxs, 
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

# def save_signal_for_matlab(signal, file_name='signal_for_matlab.txt'):
#     # Save the signal to a text file in a format MATLAB can load
#     np.savetxt(file_name, signal, delimiter=',')
#     print(f"Signal saved to {file_name} for MATLAB.")
#
# Example usage:
df = generate_test_input(plotting = False, random_data = False)
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
        # Handle array elements from Octave
        o = o[0] if isinstance(o, np.ndarray) else o
        p = p[0] if isinstance(p, np.ndarray) else p
        
        o_str = (fmt % o) if (np.isscalar(o) and not np.isnan(o)) else "N/A"
        p_str = (fmt % p) if (np.isscalar(p) and not np.isnan(p)) else "N/A"
        print(f"{o_str:<15} | {p_str:<15}")

criterion = 0.001  # Threshold for finding maxima/minima
signal = df['close'].to_numpy()
min_indexes, max_indexes, maxs, mins, up_breakpoints, down_breakpoints = octave.findMaxsMins3(signal, criterion, nout = 6)
min_indexes = (min_indexes - 1).flatten()
max_indexes = (max_indexes - 1).flatten()
up_breakpoints = np.array(up_breakpoints, dtype=int).flatten() - 1
down_breakpoints = np.array(down_breakpoints, dtype=int).flatten() - 1

# Run Python implementation
py_min_idx, py_max_idx, py_maxs, py_mins, py_up, py_down = find_maxs_mins3(signal, criterion)

print("\n=== Results Comparison ===")
all_match = True
for name, oct_data, py_data in [
    ("Min indexes", min_indexes, py_min_idx),
    ("Max indexes", max_indexes, py_max_idx),
    ("Mins values", mins, py_mins),
    ("Maxs values", maxs, py_maxs),
    ("Up breakpoints", up_breakpoints, py_up),
    ("Down breakpoints", down_breakpoints, py_down)
]:
    print(f"\n{name}:")
    print("Octave:", np.array_repr(np.array(oct_data)).replace('\n', '')[:70], "...")
    print("Python:", np.array_repr(np.array(py_data)).replace('\n', '')[:70], "...")
    all_match &= compare_results(np.array(oct_data), np.array(py_data), name)

print("\n=== Final Result ===")
print("ALL OUTPUTS MATCH:", "YES" if all_match else "NO")

print("\n=== Compact Comparison Table ===")
from itertools import zip_longest
print_compact_table(min_indexes, py_min_idx, "Min Indexes")
print_compact_table(max_indexes, py_max_idx, "Max Indexes", fmt="%d")
print_compact_table(up_breakpoints, py_up, "Up Breakpoints", fmt="%d")
print_compact_table(down_breakpoints, py_down, "Down Breakpoints", fmt="%d")

# Plot comparison
plot_local(signal, 
          min_indexes, mins.flatten(), max_indexes, maxs.flatten(), up_breakpoints, down_breakpoints,
          py_min_idx, py_mins, py_max_idx, py_maxs, py_up, py_down)
