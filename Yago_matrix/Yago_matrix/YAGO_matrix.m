% EMG analysis for each subject
% INPUT: 
%Struct data from the python interface: 
%[acc age arm condition emg gyro name quat time]
% 
% 
% OUTPUT: 
% 
% 
% 
% Tiago Rodrigues
% 11/11/2019

clc; clear all; close all;
%% Load data 
pathname = '/home/bouton/Documents/MyoProject-master/Yago_matrix/Data/S9.mat';
Data = load(pathname);

%% Variables Initialization and Resampling

% Variables initialization
targetsamplerate = 150;
time = Data.time;
time = time./1000; 
emg = double(Data.emg);
condition = Data.condition;
trial = Data.trial_vector;

% Resampling all variables at 150 Hz (timer, emgr and conditionr) 
for i=1:8
    [emgr(:,i), timer] = resample(emg(:,i), time, targetsamplerate);
end
condition = double(condition);  %pass from the int structure from python to the double
conditionr = interp1(time, condition, timer,'previous');  %interpolate condition to have the same sampling frequency as timer and emgr
trial = double(trial);
trialr = interp1(time, trial, timer,'previous');  %interpolate condition to have the same sampling frequency as time and emg

%% EMG plot

% Segmentation
emg_open(:,:) = emg(condition == 1, :);
emg_close(:,:) = emg(condition == 2, :);

figure('Name','EMG data');
subplot(2,2,1:2), plot(time,emg,time,condition*10), title('Raw EMG signal','FontSize', 30)
xlabel('Time (s)','FontSize', 15);
ylabel('a.u','FontSize', 15);
subplot(223), plot(emg_open), title('Raw EMG signal, Open','FontSize', 30)
xlabel('Duration (Timestamps)','FontSize', 15);
ylabel('a.u','FontSize', 15);
subplot(224), plot(emg_close), title('Raw EMG signal, Close','FontSize', 30)
xlabel('Duration (Timestamps)','FontSize', 15);
ylabel('a.u','FontSize', 15);


% Chose corrupted trials to eliminate after visual inspection:
corrupted=[1]; %corrupted trials
trial_corr = trialr;
indx_corr = ismember( trial_corr,corrupted);
trial_corr(indx_corr) = -1;


%%  Feature extraction

% Indicators extraction for the all emg: slididing window over the emg.
% Features 3D matrix : [samples x 8 x n�features]
N = length(emgr);
windowsize = 150;  %compute features over a 1sec window
windowstep = 1;
numsteps = (N-windowsize)/windowstep;

% Sliding window over the data
for s = 1:numsteps
    % features is a [samples x 8 x n�features] 3D-matrix;
    for j = 1:8
        features_matrix(s,j,1) =  RMS(emgr(s*windowstep:s*windowstep+windowsize,j));
        features_matrix(s,j,2) =  MAV(emgr(s*windowstep:s*windowstep+windowsize,j));
        features_matrix(s,j,3) =  VAR(emgr(s*windowstep:s*windowstep+windowsize,j));
        features_matrix(s,j,4) =  ZC(emgr(s*windowstep:s*windowstep+windowsize,j),20);
        features_matrix(s,j,5) =  WAMP(emgr(s*windowstep:s*windowstep+windowsize,j),20);
    end
end
conditionr = conditionr( 1: end - windowsize); %exclude values from the windowing
trial_corr = trial_corr( 1: end - windowsize); %exclude values from the windowing

%for each individual and indicator -> divide the indicator for it's
%maximum recorded value. 
% Ex: Individual 1; Feature RMS; Electrode 1; Divide all the total RMS
% by the max registered value in Eletrode 1 of the subject.

% Rescale each features [0 1] over each feature
mins = min(reshape(features_matrix,[],size(features_matrix,3)));
maxs = max(reshape(features_matrix,[],size(features_matrix,3)));
features_offsetted = bsxfun(@minus, features_matrix, permute(mins,[1,3,2]));
features_normalized = bsxfun(@rdivide, features_offsetted, permute(maxs-mins,[1,3,2]));

%% Graphs & Stats
% Parameters: 
%n_condition 1-open; 2-close
%feature_number 1-5
n_condition = 1;
feature_number = 1; 

for i=1:2
    mean(:,:,i) = nanmean(features_normalized(conditionr==i,:,:),1);
end

figure(1)
subplot(211), heatmap(mean(:,:,1)), title('Open')
subplot(212), heatmap(mean(:,:,2)) ,title('Close')

figure(2)
plot(features_normalized(and(conditionr == n_condition,trial_corr~=-1),:,feature_number));
legend('1','2','3','4','5','6','7','8')
feature_name = {'RMS','MAV','VAR','ZC','WAMP'};  
n_name = {'Open','Close'};
title(strcat(n_name(n_condition),'+',feature_name(feature_number)));


figure(3)
labels = {'RMS','MAV','VAR','ZC','WAMP'};
groups = [1,2,3,4,5,6,7,8];
subplot(211), parallelcoords(mean(:,:,1),'group', groups,'Labels',labels), title('Open');
ylim([0 1])
subplot(212), parallelcoords(mean(:,:,2),'group', groups,'Labels',labels), title('Close');
ylim([0 1])


%% Frequency domain
for i=1:8
    [P_open, f_open] = pwelch(emgr(and(conditionr == 1,trial_corr~=-1),i)-nanmean(emgr(:,i)),300, [], 4000, 150);
    subplot(221), plot(f_open,P_open,'linewidth',2);
    hold on
    title('PSD Open')
    [P_close, f_close] = pwelch(emgr(and(conditionr == 2,trial_corr~=-1),i)-nanmean(emgr(:,i)),300, [], 4000, 150);
    subplot(222), plot(f_close,P_close,'linewidth',2);
    hold on
    title('PSD Close')
    subplot(223), [Par_open, f_ar] = AR_psd(emgr(and(conditionr == 2,trial_corr~=-1),i),20,1,0.5,0,1); %db=0 -> linear
    hold on
    title('Estimated PSD (AR-model) Open')
    subplot(224), [Par_open, f_ar] = AR_psd(emgr(and(conditionr == 2,trial_corr~=-1),i),20,1,0.5,0,1); %db=0 -> linear
    hold on
    title('Estimated PSD (AR-model) Close')
end
legend('1','2','3','4','5','6','7','8')
