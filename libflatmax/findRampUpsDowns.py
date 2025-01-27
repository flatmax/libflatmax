import numpy as np
from .findMaxsMins3 import find_maxs_mins3

def find_ramp_ups(signal, criterion):
    """
    Find ramp-ups by analyzing signal with positive offset
    
    Parameters:
    signal : array_like
        Input signal vector to analyze
    criterion : float
        Threshold value for finding maxima/minima (0-1)
    
    Returns:
    tuple: (min_indexes, max_indexes, maxs, mins, up_breakpoints, down_breakpoints)
        min_indexes - Indices of local minima
        max_indexes - Indices of local maxima  
        maxs - Values at local maxima
        mins - Values at local minima
        up_breakpoints - Indices where signal rises above threshold
        down_breakpoints - Indices where signal falls below threshold
    
    Raises:
    ValueError: For invalid input arguments
    """
    # Input validation
    if not isinstance(signal, (np.ndarray, list)):
        raise ValueError("signal must be a numpy array or list")
    if not isinstance(criterion, (int, float)) or not 0 <= criterion <= 1:
        raise ValueError("criterion must be a numeric scalar between 0 and 1")
    
    signal = np.asarray(signal).flatten()
    
    # Shift signal to ensure positive values
    signal_min = np.min(signal)
    signal_in = signal - signal_min + 1
    
    # Find extrema using shifted signal
    (min_indexes, max_indexes, 
     _, _,  # Discard shifted signal's values
     up_breakpoints, down_breakpoints) = find_maxs_mins3(signal_in, criterion)
    
    # Map back to original signal values using found indexes
    maxs = signal[max_indexes] if len(max_indexes) > 0 else np.array([])
    mins = signal[min_indexes] if len(min_indexes) > 0 else np.array([])
    
    return (min_indexes, max_indexes, maxs, mins, 
            up_breakpoints, down_breakpoints)
