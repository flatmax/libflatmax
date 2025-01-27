function [minIndexes, maxIndexes, maxs, mins, upBreakPoints, downBreakPoints] = findRampUps(signal, criterion)
% Find ramp-ups by analyzing signal with positive offset
%
% Inputs:
%   signal - Input signal vector to analyze
%   criterion - Threshold value for finding maxima/minima
%
% Outputs:
%   minIndexes - Indices of local minima
%   maxIndexes - Indices of local maxima
%   maxs - Values at local maxima
%   mins - Values at local minima
%   upBreakPoints - Indices where signal rises above threshold
%   downBreakPoints - Indices where signal falls below threshold

% Input validation
if nargin < 2
    error('findRampUps requires both signal and criterion inputs');
end
if ~isnumeric(signal) || ~isvector(signal)
    error('signal must be a numeric vector');
end
if ~isnumeric(criterion) || ~isscalar(criterion)
    error('criterion must be a numeric scalar');
end

% Shift signal to ensure positive values
signalIn = signal - min(signal) + 1;

% Call existing implementation with modified signal
[minIndexes, maxIndexes, ~, ~, upBreakPoints, downBreakPoints] = ...
    findMaxsMins3(signalIn, criterion);

% Extract actual values from original signal using found indexes
maxs = signal(maxIndexes);
mins = signal(minIndexes);
end
