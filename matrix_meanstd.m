function [meanRMS, stdRMS] = matrix_meanstd(features,conditionr,n,plot)
% Input:
% features, features matrix rescaled [0 1] 
% conditionr, resampled condition vector
% n, number of trials
% plot = 1 to plot the results
% 
% Output:
% [meanRMS; stdRMS] 
% meanRMS = [meanopen meanclose] 8x2 (8 eletrodes and 2 conditions)
% stdRMS =  [stdopen stdclose] 8x2 (8eletrodes and 2conditions)

% For each emg channel, split the trials into open and close (later add
%open+myo and close+myo). 
%For each condition (open or close): compute the mean and standard
%deviation over the n trials -> plot using mean and stshade.
targetsamplerate = 150;
ws = 150; %windowsize, to remove initial and last portions of the emg signal

 
% Conditions vector
open = (conditionr == 1 | conditionr == 3);
clos = (conditionr == 2 | conditionr == 4);

%Dividing all 'activations' in the different n trials -> compute mean and
%standard deviation from each trial
openlength = length(find(open>0));    % length of the open trials
iopen = openlength + (n -rem(openlength,n)); % get a total dataset divisible by n (10), to perform reshape
    
closelength = length(find(clos>0));   %length of the close trials
iclos = closelength + (n - rem(closelength,n));
% need to do this because the number of 'closes and opens' varies from
% resampling the condition vector, feel the dataset until it is divisible
% by the number of trials (n).

if plot == 1
    figure
end

for i=1:8
    %computing the features for the all EMG vector
    RMStotal = features((i-1)*5 +1, :); %get the feature correspondent from the function features
    RMSopen = RMStotal(open);
    RMSclose = RMStotal(clos);
    
    %dividing all the emg in specific conditions -> followed by division in
    %specific trials (each trial set as a collumn)
    RMSopenfull = zeros(1,iopen);  RMSopenfull(1:openlength) = RMSopen;
    RMSopen_divided = reshape(RMSopenfull, iopen/n,[]);  % [750 x n] matrix where n is the number of trials and 750 'duration' of the trial (in samples)
    RMSopen_divided(RMSopen_divided == 0) = NaN;
    RMSopen_divided = RMSopen_divided(ws/2:end-ws/2,:);
    
    RMSclosefull = zeros(1,iclos); RMSclosefull(1:closelength) = RMSclose;
    RMSclose_divided = reshape(RMSclosefull, iclos/n,[]);  % [750 x n] matrix where n is the number of trials and 750 'duration' of the trial (in samples)
    RMSclose_divided(RMSclose_divided == 0) = NaN; 
    RMSclose_divided = RMSclose_divided(ws/2:end-ws/2,:);
    

    MAVtotal = features((i-1)*5 +2, :); 
    MAVopen = MAVtotal(open);
    MAVclose = MAVtotal(clos);
    
    MAVopenfull = zeros(1,iopen); MAVopenfull(1:openlength) = MAVopen;
    MAVopen_divided = reshape(MAVopenfull, iopen/n,[]); 
    
    MAVclosefull = zeros(1,iclos); MAVclosefull(1:closelength) = MAVclose;
    MAVclose_divided = reshape(MAVclosefull, iclos/n,[]); 
    
    
    
    VARtotal = features((i-1)*5 +3, :);
    VARopen = VARtotal(open);
    VARclose = VARtotal(clos);
    
    VARopenfull = zeros(1,iopen); VARopenfull(1:openlength) = VARopen;
    VARopen_divided = reshape(VARopenfull, iopen/n,[]); 
    
    VARclosefull = zeros(1,iclos); VARclosefull(1:closelength) = VARclose;
    VARclose_divided = reshape(VARclosefull, iclos/n,[]); 
    
    
    ZCtotal = features((i-1)*5 +4, :);
    ZCopen = ZCtotal(open);
    ZCclose = ZCtotal(clos);
    
    ZCopenfull = zeros(1,iopen); ZCopenfull(1:openlength) = ZCopen;
    ZCopen_divided = reshape(ZCopenfull, iopen/n,[]); 
    
    ZCclosefull = zeros(1,iclos); ZCclosefull(1:closelength) = RMSclose;
    ZCclose_divided = reshape(ZCclosefull, iclos/n,[]);  
    
    
    WAMPtotal = features((i-1)*5 +5, :);
    WAMPopen = WAMPtotal(open);
    WAMPclose = WAMPtotal(clos);
    
    WAMPopenfull = zeros(1,iopen); WAMPopenfull(1:openlength) = WAMPopen;
    WAMPopen_divided = reshape(WAMPopenfull, iopen/n,[]);  
    
    WAMPclosefull = zeros(1,iclos); WAMPclosefull(1:closelength) = RMSclose;
    WAMPclose_divided = reshape(WAMPclosefull, iclos/n,[]);  

    timeopen = 1/targetsamplerate :  1/targetsamplerate : length(RMSopen_divided)/targetsamplerate;
    timeclose = 1/targetsamplerate :  1/targetsamplerate : length(RMSclose_divided)/targetsamplerate;     
    
    meanopen(i) = nanmean(RMSopen_divided,'all');
    %standard deviation across dimention 1
    stdopen_vector = nanstd(RMSopen_divided,0,1);
    %mean of the std for each trial
    stdopen(i) = nanmean(stdopen_vector ); 
    
    meanclose(i) = nanmean(RMSclose_divided,'all');
    %standard deviation across dimention 1, ignoring nan values
    stdclose_vector = nanstd(RMSclose_divided,0,1); 
    %mean of the std for each trial
    stdclose(i) = nanmean(stdclose_vector ); 

    meanRMS= [meanopen' meanclose'];
    stdRMS = [stdopen' stdclose'];
    
    if plot == 1
        subplot(4,2,i), stdshade(RMSopen_divided',0.2,'blue',timeopen); 
        hold on
        subplot(4,2,i), stdshade(RMSclose_divided',0.2,'red',timeclose);
        
        muscles = {'Flexor Carpi Ulnaris','Flexor carpi ulnaris','Extensor carpi ulnaris','Extensor digitorum','Extensor carpi radialis','Extensor carpi radialis lungus','Brachiocardialis','Flexor digitorum Profundus'};  % to plot in the graph
        title(muscles(i))
        xlabel('Time(s)');
        ylabel('a.u')
        legend('std open', 'RMS mean open','std close','RMS mean close');
    
    end
end
 
end

