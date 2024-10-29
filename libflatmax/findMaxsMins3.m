function [minIndexes, maxIndexes, maxs, mins, upBreakPoints, downBreakPoints]=findMaxsMins3(signal,criterion)
% find maxes and mins with criterion as the threshold

% Copyright 2011-2024 Matt Flax Flatmax Pty Ltd
% Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
% The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
% THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

% for into a column vector
[r,c]=size(signal);
if c>r signal=signal'; end

N=length(signal);

maximum=max(signal); % maximum point.
globalMaxIndex=find(signal==maximum);
globalMaxIndex=globalMaxIndex(1);

minIndexes=[];
mins=[];

% start at the global max and work up ....
index=1;
maxIndexes=[]; maxs=[];
[minIndexes, mins, maxIndexes,maxs]=computeMaxsMins(signal,N,index,criterion,minIndexes, mins, maxIndexes,maxs);

try
    if minIndexes(1:2)<maxIndexes(1)
        if length(minIndexes)>length(maxIndexes)
            minIndexes(1)=[]; mins(1)=[];
        else
            error('here 20')
        end
        if minIndexes(1:2)<maxIndexes(1)
            error('here22')
        end
    elseif maxIndexes(1:2)<minIndexes(1)
        if length(maxIndexes)>length(minIndexes)
            maxIndexes(1)=[]; maxs(1)=[];
        else
            error('here 21')
        end
        if maxIndexes(1:2)<minIndexes(1)
            error('here23')
        end
    end
catch
%     minIDXs=minIndexes
%     maxIDXs=maxIndexes
%     fprintf('problem looking at mins and maxs\n')
minIndexes=[]; maxIndexes=[]; 
maxs=[]; mins=[]; upBreakPoints=[]; downBreakPoints=[];
return
end

% find breakpoints
[upBreakPoints, downBreakPoints]=findBreakPoints(minIndexes,maxIndexes,signal,criterion);

% stats.minPriceIndexes=minIndexes;
% stats.maxPriceIndexes=maxIndexes;
% stats.maxPrices=maxs;
% stats.minPrices=mins;
% stats.upBreakPoints = upBreakPoints;
% stats.downBreakPoints = downBreakPoints;
% stats.prices=signal;

% if the last break point is smaller then the criterion, then trim the last max or min
if downBreakPoints(end)<maxIndexes(end)
    maxIndexes=maxIndexes(1:end-1);
    maxs=maxs(1:end-1);
%     disp('last down breakpoint is < last max index 1');
end
if 1-signal(downBreakPoints(end))/signal(maxIndexes(end)) < criterion-eps
%     disp('last down breakpoint is < last max index 2');
    maxIndexes=maxIndexes(1:end-1);
    maxs=maxs(1:end-1);
    downBreakPoints=downBreakPoints(1:end-1);
end
% disp(' ');

if upBreakPoints(end)<minIndexes(end)
    minIndexes=minIndexes(1:end-1);
    mins=mins(1:end-1);
    disp('last up breakpoint is < last min index');
end
if signal(upBreakPoints(end))/signal(minIndexes(end))-1 < criterion-eps
    disp('removing last min as no valid break point found')
    minIndexes=minIndexes(1:end-1);
    mins=mins(1:end-1);
    upBreakPoints=upBreakPoints(1:end-1);
end

plotting=0;

if plotting
    plotLocal(signal, minIndexes, mins, maxIndexes, maxs, upBreakPoints, downBreakPoints)
end
'out here'
end

function plotLocal(signal, minIndexes, mins, maxIndexes, maxs, upBreakPoints, downBreakPoints)
    clf
    plot(signal); hold on
    plot(minIndexes,mins, 'go');
    plot(upBreakPoints,signal(upBreakPoints), 'g*');
    plot(maxIndexes,maxs, 'ro');
    plot(downBreakPoints,signal(downBreakPoints), 'r*');
    hold off
    grid
end

function [minIndexes, mins, maxIndexes,maxs]=computeMaxsMins(signal,N,index,criterion,minIndexes, mins, maxIndexes,maxs)
persistent oldSignal
persistent matrix
persistent pcts
if isempty(oldSignal)
	matrix=hankel(signal);
	pcts=matrix./repmat(signal',N,1); % % wrt to each point
	oldSignal=signal;
end
if any(size(oldSignal) ~= size(signal)) || any(oldSignal~=signal)
	matrix=hankel(signal);
	pcts=matrix./repmat(signal',N,1); % % wrt to each point
	oldSignal=signal;
end

% find where to start
try
    comp1=@le; comp2=@ge; comp3=@lt; walkFn=@walkDown; minOrMax=@min;
    indexMin=findMinOrMax(pcts,index,criterion,comp1,comp2,comp3,minOrMax,walkFn,signal); % find the min
catch
    indexMin=length(signal);
end
try
    comp1=@ge; comp2=@le; comp3=@gt; walkFn=@walkUp; minOrMax=@max;
    indexMax=findMinOrMax(pcts,index,-criterion,comp1,comp2,comp3,minOrMax,walkFn,signal); % find the max
catch
    indexMax=length(signal);
end
    if indexMin==-1 indexMin=length(signal); end
    if indexMax==-1 indexMax=length(signal); end

if indexMin<indexMax
    index=indexMin;
    minIndexes=[minIndexes index]; % remember the minIndex
    mins=[mins signal(index)]; % remember the price at this min

    % if the first index is a min - ensure we look for a max next
    comp1=@ge; comp2=@le; comp3=@gt; walkFn=@walkUp; minOrMax=@max;
    index=findMinOrMax(pcts,index,-criterion,comp1,comp2,comp3,minOrMax,walkFn,signal); % find the max
    
    maxIndexes=[maxIndexes index]; % remember the minIndex
    maxs=[maxs signal(index)]; % remember the price at this min
else
    index=indexMax;
    maxIndexes=[maxIndexes index]; % remember the minIndex
    try
    maxs=[maxs signal(index)]; % remember the price at this min
    catch
        error('here2')
    end
end

while index<N
    comp1=@le; comp2=@ge; comp3=@lt; walkFn=@walkDown; minOrMax=@min;
    index=findMinOrMax(pcts,index,criterion,comp1,comp2,comp3,minOrMax,walkFn,signal); % find the min
    if index<0 % stopping criterion
        break;
    end
    
    minIndexes=[minIndexes index]; % remember the minIndex
    mins=[mins signal(index)]; % remember the price at this min
    %plot(minIndexes(end),signal(minIndexes(end)),'go')

    comp1=@ge; comp2=@le; comp3=@gt; walkFn=@walkUp; minOrMax=@max;
    index=findMinOrMax(pcts,index,-criterion,comp1,comp2,comp3,minOrMax,walkFn,signal); % find the max
    if index<0 % stopping criterion
        break;
    end
    
    maxIndexes=[maxIndexes index]; % remember the minIndex
    maxs=[maxs signal(index)]; % remember the price at this min
    %plot(maxIndexes(end),signal(maxIndexes(end)),'ro')
end
%plot(minIndexes,minIndexes,'*'); hold on; plot(maxIndexes,maxIndexes,'*r'); hold off
end

function index=walkDown(pcts,index)
localIndexes=find(pcts(:,index)<1);
j=2;
while j<=length(localIndexes) % walk down to the bottom
    if localIndexes(j-1)==j
        index=index+1;
        localIndexes=find((pcts(:,index)<1)&(pcts(:,index)>0));
        j=2;
    else
        break;
    end
end
end

function index=walkUp(pcts,index)
localIndexes=find(pcts(:,index)>1);
j=2;
while j<=length(localIndexes) % walk down to the bottom
    if localIndexes(j-1)==j
        index=index+1;
        localIndexes=find(pcts(:,index)>1);
        j=2;
    else
        break;
    end
end
end

function index=findMinOrMax(pcts,index,criterion,comp1,comp2,comp3,minOrMax,walkFn,signal)
%localIndexes=find(pcts(:,index)<=1-criterion);
localIndexes=find(comp1(pcts(:,index),1-criterion));
try
    if ~isempty(localIndexes)
    index=index+localIndexes(1)-1;
    end
catch
    error('here16')
end
if index>=length(signal)
    index=-1;
    return; % this is a stopping criterion
end
% check there is nothing smaller before the next max
try
    index=walkFn(pcts,index);
catch
    error('here17')
end
% plot(index,signal(index),'g+')

localIndexes=[];
while isempty(localIndexes)
    % find the next 1+criterion point
    %localIndexes=find(pcts(:,index)>=1+criterion);
    localIndexes=find(comp2(pcts(:,index),1+criterion));
    if isempty(localIndexes) % at the edge
        % we must increment and walk down
        %localIndex=find(pcts(:,index)<1);
        localIndex=find(comp3(pcts(:,index),1)&(pcts(:,index)>0));
        if isempty(localIndex) | index+localIndex>=length(pcts)
            index=-1;
            return; % this is a stopping criterion
        end
        try
            index=walkFn(pcts,index+localIndex(1));
        catch
            error('here18')
        end
        %localIndexes=find(pcts(:,index)>=1+criterion);
        localIndexes=find(comp2(pcts(:,index),1+criterion));
    end
    if index>length(signal) error('stopping criterion'); end
end
% check there is nothing less then our current local between here and there.
% check there is nothing smaller before the next max
%checkIndexes=find(pcts(1:localIndexes(1),index)<1);
checkIndexes=find(comp3(pcts(1:localIndexes(1),index),1));
while ~isempty(checkIndexes)
    localIndex=find(comp3(pcts(:,index),1))-1;
    if isempty(localIndex)
        index=-1;
        return; % this is a stopping criterion
    end
    index=walkFn(pcts,index+localIndex(1));
    %localIndexes=find(pcts(:,index)>=1+criterion);
    localIndexes=find(comp2(pcts(:,index),1+criterion));
    checkIndexes=find(comp3(pcts(1:localIndexes(1),index),1));
end
% if ~isempty(checkIndexes)
%     localIndexes=checkIndexes(find(pcts(checkIndexes,index)==minOrMax(pcts(checkIndexes,index))))-1;
%     index=index+localIndexes(1);
%     %checkIndexes=find(pcts(1:localIndexes(1),index)<1);
%     checkIndexes=find(comp3(pcts(1:localIndexes(1),index),1));
%     if ~isempty(checkIndexes)
%         error('this probably needs to be a recursion')
%     end
% end
end

function [upBreakPoints, downBreakPoints]=findBreakPoints(minIndexes,maxIndexes,signal,criterion)
upBreakPoints=[];
downBreakPoints=[];
for i=1:length(minIndexes)
    index=minIndexes(i)+1;
    thresh=signal(minIndexes(i))*(1+criterion);
    while index<length(signal) & (signal(index)+eps)<thresh
        index=index+1;
    end
    if index<=length(signal)
        upBreakPoints(end+1)=index;
    end
end
for i=1:length(maxIndexes)
    index=maxIndexes(i)+1;
    thresh=signal(maxIndexes(i))*(1-criterion);
    while index<length(signal) & (signal(index)-eps)>thresh
        index=index+1;
    end
    if index<=length(signal)
        downBreakPoints(end+1)=index;
    end
end
end
