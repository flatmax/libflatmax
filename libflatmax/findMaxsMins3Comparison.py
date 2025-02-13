#!/usr/bin/env python

from libflatmax.comparison_utils import (
    generate_test_input,
    run_comparison_test,
    plot_comparison,
    print_compact_table
)
from libflatmax.findMaxsMins3 import find_maxs_mins3
from oct2py import octave

# Load test data
df = generate_test_input(plotting=False, random_data=False)
criterion = 0.001
signal = df['close'].to_numpy()

# Run main comparison
all_match = run_comparison_test(
    octave_fn=octave.findMaxsMins3,
    python_fn=find_maxs_mins3,
    signal=signal,
    criterion=criterion,
    test_name="findMaxsMins3"
)
# Inverted signal test
print("\n=== Running Inverted Signal Test ===")
inverted_signal = -signal

# Run inverted comparison
inv_match = run_comparison_test(
    octave_fn=octave.findMaxsMins3,
    python_fn=find_maxs_mins3,
    signal=inverted_signal,
    criterion=criterion,
    test_name="Inverted Signal findMaxsMins3"
)

print("\n=== All Tests Summary ===")
print("Original signal match:", "YES" if all_match else "NO")
print("Inverted signal match:", "YES" if inv_match else "NO")
