import numpy as np

def find_maxs_mins3(signal, criterion, plotting=False):
    signal = np.array(signal).flatten()
    N = len(signal)
    if N == 0:
        return [], [], [], [], [], []
    
    # Ensure column vector
    if len(signal.shape) == 1:
        signal = signal.reshape(-1, 1)
    
    # Find global maximum
    max_val = np.max(signal)
    global_max_index = np.argmax(signal)
    
    # Initialize variables
    min_indexes = []
    mins = []
    max_indexes = []
    maxs = []
    
    # Create Hankel matrix and pcts
    hankel = np.zeros((N, N))
    for i in range(N):
        hankel[i, :N-i] = signal[i:].flatten()
    tiled_signal = np.tile(signal.T, (N, 1))
    pcts = np.divide(hankel, tiled_signal, where=tiled_signal!=0)
    
    # Compute maxima/minima
    min_indexes, mins, max_indexes, maxs = compute_maxs_mins(
        signal, N, 0, criterion, hankel, pcts, min_indexes, mins, max_indexes, maxs
    )
    
    # Error checking for initial sequence
    try:
        if len(min_indexes) >= 2 and len(max_indexes) >= 1:
            if min_indexes[0] < max_indexes[0] and min_indexes[1] < max_indexes[0]:
                if len(min_indexes) > len(max_indexes):
                    min_indexes = min_indexes[1:]
                    mins = mins[1:]
                else:
                    raise Exception("here 20")
                if min_indexes[0] < max_indexes[0] and min_indexes[1] < max_indexes[0]:
                    raise Exception("here22")
        elif len(max_indexes) >= 2 and len(min_indexes) >= 1:
            if max_indexes[0] < min_indexes[0] and max_indexes[1] < min_indexes[0]:
                if len(max_indexes) > len(min_indexes):
                    max_indexes = max_indexes[1:]
                    maxs = maxs[1:]
                else:
                    raise Exception("here 21")
                if max_indexes[0] < min_indexes[0] and max_indexes[1] < min_indexes[0]:
                    raise Exception("here23")
    except Exception as e:
        return [], [], [], [], [], []
    
    # Find breakpoints
    up_breakpoints, down_breakpoints = find_break_points(
        min_indexes, max_indexes, signal, criterion
    )
    
    # Post-processing of results
    if down_breakpoints and max_indexes and down_breakpoints[-1] < max_indexes[-1]:
        max_indexes = max_indexes[:-1]
        maxs = maxs[:-1]
        
    if down_breakpoints and max_indexes and (1 - signal[down_breakpoints[-1]]/signal[max_indexes[-1]] < criterion - np.finfo(float).eps):
        max_indexes = max_indexes[:-1]
        maxs = maxs[:-1]
        down_breakpoints = down_breakpoints[:-1]
        
    if up_breakpoints and min_indexes and up_breakpoints[-1] < min_indexes[-1]:
        min_indexes = min_indexes[:-1]
        mins = mins[:-1]
        
    if up_breakpoints and min_indexes and (signal[up_breakpoints[-1]]/signal[min_indexes[-1]] - 1 < criterion - np.finfo(float).eps):
        min_indexes = min_indexes[:-1]
        mins = mins[:-1]
        up_breakpoints = up_breakpoints[:-1]
    
    if plotting:
        plot_local(signal, min_indexes, mins, max_indexes, maxs, up_breakpoints, down_breakpoints)
    
    return min_indexes, max_indexes, maxs, mins, up_breakpoints, down_breakpoints

def compute_maxs_mins(signal, N, index, criterion, hankel, pcts, min_indexes, mins, max_indexes, maxs):
    # Find initial min
    try:
        comp1 = lambda x, y: x <= y
        comp2 = lambda x, y: x >= y
        comp3 = lambda x, y: x < y
        index_min = find_min_or_max(pcts, index, criterion, comp1, comp2, comp3, np.min, walk_down, signal)
    except:
        index_min = N
    
    # Find initial max
    try:
        comp1 = lambda x, y: x >= y
        comp2 = lambda x, y: x <= y
        comp3 = lambda x, y: x > y
        index_max = find_min_or_max(pcts, index, -criterion, comp1, comp2, comp3, np.max, walk_up, signal)
    except:
        index_max = N
    
    index_min = index_min if index_min != -1 else N
    index_max = index_max if index_max != -1 else N
    
    if index_min < index_max:
        index = index_min
        min_indexes.append(index)
        mins.append(signal[index])
        
        # Find subsequent max
        index = find_min_or_max(pcts, index, -criterion, 
                              lambda x,y: x>=y, lambda x,y: x<=y, lambda x,y: x>y,
                              np.max, walk_up, signal)
        max_indexes.append(index)
        maxs.append(signal[index])
    else:
        index = index_max
        max_indexes.append(index)
        maxs.append(signal[index])
    
    # Main processing loop
    while index < N-1:
        # Find next min
        index = find_min_or_max(pcts, index, criterion, 
                              lambda x,y: x<=y, lambda x,y: x>=y, lambda x,y: x<y,
                              np.min, walk_down, signal)
        if index < 0 or index >= N:
            break
        min_indexes.append(index)
        mins.append(signal[index])
        
        # Find next max
        index = find_min_or_max(pcts, index, -criterion, 
                              lambda x,y: x>=y, lambda x,y: x<=y, lambda x,y: x>y,
                              np.max, walk_up, signal)
        if index < 0 or index >= N:
            break
        max_indexes.append(index)
        maxs.append(signal[index])
    
    return min_indexes, mins, max_indexes, maxs

def walk_down(pcts, index):
    local_indexes = np.where(pcts[:, index] < 1)[0]
    j = 1
    while j < len(local_indexes):
        if local_indexes[j-1] == j-1:
            index += 1
            if index >= pcts.shape[1]:
                return index
            local_indexes = np.where((pcts[:, index] < 1) & (pcts[:, index] > 0))[0]
            j = 1
        else:
            break
    return index

def walk_up(pcts, index):
    local_indexes = np.where(pcts[:, index] > 1)[0]
    j = 1
    while j < len(local_indexes):
        if local_indexes[j-1] == j-1:
            index += 1
            if index >= pcts.shape[1]:
                return index
            local_indexes = np.where(pcts[:, index] > 1)[0]
            j = 1
        else:
            break
    return index

def find_min_or_max(pcts, index, criterion, comp1, comp2, comp3, min_or_max, walk_fn, signal):
    if index >= pcts.shape[1]:
        return -1
    
    target = 1 + criterion
    local_indexes = np.where(comp1(pcts[:, index], target))[0]
    
    if len(local_indexes) > 0:
        index += local_indexes[0]
    
    if index >= len(signal):
        return -1
    
    try:
        index = walk_fn(pcts, index)
    except:
        return -1
    
    if index >= len(signal):
        return -1
    
    local_indexes = np.where(comp2(pcts[:, index], 1 + criterion))[0]
    while len(local_indexes) == 0:
        local_index = np.where(comp3(pcts[:, index], 1))[0]
        if len(local_index) == 0 or index + local_index[0] >= len(signal):
            return -1
        index += local_index[0]
        try:
            index = walk_fn(pcts, index)
        except:
            return -1
        local_indexes = np.where(comp2(pcts[:, index], 1 + criterion))[0]
    
    check_indexes = np.where(comp3(pcts[:local_indexes[0]+1, index], 1))[0]
    while len(check_indexes) > 0:
        local_index = np.where(comp3(pcts[:, index], 1))[0]
        if len(local_index) == 0:
            return -1
        index += local_index[0]
        local_indexes = np.where(comp2(pcts[:, index], 1 + criterion))[0]
        check_indexes = np.where(comp3(pcts[:local_indexes[0]+1, index], 1))[0]
    
    return index

def find_break_points(min_indexes, max_indexes, signal, criterion):
    up_breakpoints = []
    for i in range(len(min_indexes)):
        index = min_indexes[i] + 1
        thresh = signal[min_indexes[i]] * (1 + criterion)
        while index < len(signal) and (signal[index] + np.finfo(float).eps) < thresh:
            index += 1
        if index < len(signal):
            up_breakpoints.append(index)
    
    down_breakpoints = []
    for i in range(len(max_indexes)):
        index = max_indexes[i] + 1
        thresh = signal[max_indexes[i]] * (1 - criterion)
        while index < len(signal) and (signal[index] - np.finfo(float).eps) > thresh:
            index += 1
        if index < len(signal):
            down_breakpoints.append(index)
    
    return up_breakpoints, down_breakpoints

def plot_local(signal, min_indexes, mins, max_indexes, maxs, up_breakpoints, down_breakpoints):
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(signal)
    plt.plot(min_indexes, mins, 'go')
    plt.plot(up_breakpoints, signal[up_breakpoints], 'g*')
    plt.plot(max_indexes, maxs, 'ro')
    plt.plot(down_breakpoints, signal[down_breakpoints], 'r*')
    plt.grid(True)
    plt.show()
