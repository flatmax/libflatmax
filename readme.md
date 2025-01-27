# libflatmax

## Installation

```
conda create -n libflatmax
conda activate libflatmax
pip install -e .
```

## Algorithm Documentation

### `findMaxsMins3`
Core algorithm for finding significant local maxima/minima in signals.

**Key Features:**
- Identifies extrema using a threshold-based approach
- Handles both positive and negative signal values
- Returns:
  - Indexes/values of local minima
  - Indexes/values of local maxima  
  - Up/Down breakpoints (transition points between trends)
  
**Parameters:**
- `signal`: Input time series data
- `criterion`: Threshold for minima/maxima detection (0-1, percentage-based)

**Implementation:**
- MATLAB and Python implementations maintained in parity
- Validated through `findMaxsMins3Comparison.py` test script

### `findRampUpsDowns` 
Specialized version for detecting ramp-up/down patterns in signals, no matter if they are positive, negative or mixed signals.

**Key Differences from Base Algorithm:**
- Pre-processes signal to ensure positivity before analysis
- Focused on identifying sustained upward/downward trends
- Preserves original signal values in outputs
- Particularly effective for:
  - Trend following strategies
  - Breakout detection
  - Momentum analysis

**Parameters:**
- Same interface as `findMaxsMins3` but optimized for trend detection
- Validated through `findRampUpsDownsComparison.py` test script

**Relationship to Base Algorithm:**
- Uses `findMaxsMins3` internally after signal normalization
- Adds post-processing to map results back to original signal values
- Maintains same return structure but with trend-focused breakpoints

## Validation
Comparison scripts (`*Comparison.py`) verify parity between:
- MATLAB/Octave reference implementations
- Python/numpy optimized versions
- Includes visual comparisons and numerical validation
