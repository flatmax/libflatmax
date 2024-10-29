#!/usr/bin/env python

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from findMaxsMins3 import find_maxs_mins
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


def plot_local(signal, min_indexes, mins, max_indexes, maxs, up_breakpoints, down_breakpoints):
    # Clear the current figure
    plt.clf()

    # Plot the main signal
    plt.plot(signal, label="Signal", color="blue")

    # Plot minimum points as green circles
    plt.plot(min_indexes, mins, 'go', label="Min Points")

    # Plot up breakpoints as green stars
    plt.plot(up_breakpoints, [signal[i] for i in up_breakpoints], 'g*', label="Up Breakpoints")

    # Plot maximum points as red circles
    plt.plot(max_indexes, maxs, 'ro', label="Max Points")

    # Plot down breakpoints as red stars
    plt.plot(down_breakpoints, [signal[i] for i in down_breakpoints], 'r*', label="Down Breakpoints")

    # Display grid and legend
    plt.grid(True)

    # Show the plot
    plt.show()

# def save_signal_for_matlab(signal, file_name='signal_for_matlab.txt'):
#     # Save the signal to a text file in a format MATLAB can load
#     np.savetxt(file_name, signal, delimiter=',')
#     print(f"Signal saved to {file_name} for MATLAB.")
#
# Example usage:
df = generate_test_input(plotting = False, random_data = False)
criterion = 0.001  # Example criterion
#
# save_signal_for_matlab(signal, file_name='signal_for_matlab.txt')
# save_signal_for_matlab(cirterion, file_name='signal_for_matlab_criterion.txt')
#
# # Run comparison
# print(df)
# comparison_results = compare_results(df['price'], criterion)
# print(df['close'].to_numpy())
# comparison_results = compare_results(df['close'].to_numpy(), criterion)
# print(comparison_results)
signal = df['close'].to_numpy()
min_indexes, max_indexes, maxs, mins, up_breakpoints, down_breakpoints = octave.findMaxsMins3(signal, criterion, nout = 6)
min_indexes=min_indexes-1
max_indexes=max_indexes-1
up_breakpoints=np.array(up_breakpoints, dtype=int)-1
down_breakpoints=np.array(down_breakpoints, dtype=int)-1

# Print or use the outputs as needed
# print("Min indexes:", min_indexes)
# print("Max indexes:", max_indexes)
# print("Max values:", maxs)
# print("Min values:", mins)
# print("Up breakpoints:", up_breakpoints)
# print("Down breakpoints:", down_breakpoints)

plot_local(signal, min_indexes, mins, max_indexes, maxs, up_breakpoints, down_breakpoints)