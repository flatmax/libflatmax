#!/usr/bin/env python

from libflatmax.comparison_utils import (
    generate_test_input,
    run_comparison_test,
    plot_comparison,
    print_compact_table
)
from libflatmax.findRampUpsDowns import find_ramp_ups
from oct2py import octave

# Load test data
df = generate_test_input(plotting=False, random_data=False)
criterion = 0.001
signal = df['close'].to_numpy()

# Run main comparison
all_match = run_comparison_test(
    octave_fn=octave.findRampUpsDowns,
    python_fn=find_ramp_ups,
    signal=signal,
    criterion=criterion,
    test_name="findRampUpsDowns"
)

# Inverted signal test
print("\n=== Running Inverted Signal Test ===")
inverted_signal = -signal

# Run inverted comparison
inv_match = run_comparison_test(
    octave_fn=octave.findRampUpsDowns,
    python_fn=find_ramp_ups,
    signal=inverted_signal,
    criterion=criterion,
    test_name="Inverted Signal findRampUpsDowns"
)

print("\n=== All Tests Summary ===")
print("Original signal match:", "YES" if all_match else "NO")
print("Inverted signal match:", "YES" if inv_match else "NO")
