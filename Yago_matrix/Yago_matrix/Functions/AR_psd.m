function [Px,fr] = AR_psd(x,p,fe,fmax,db,Aff);

% [Px,fr] = AR_psd(x,p,fe,fmax,db);
% parametric spectral density estimation
% p model order
% fe sampling frequency
% fmax maximum frequency for plot
% db = 0 linear plot, otherwise dB plot
% Px spectral density estimate (up to fmax)
% fr frequency values (up to fmax)
% Aff=1 display

Nf = 2000;

% model estimation
[a,e] = aryule(x,p);

% psd estimation
[G,f] = freqz(1,a,Nf);
Px = 2*e*(abs(G).^2)/fe;
f = fe*f/2/pi;
Ind = find(f<=fmax);
fr = f(Ind);
Px = Px(Ind);
if Aff==1,
if db==0,
   plot(fr,Px,'LineWidth',2);
   ylabel('linear')
else
   plot(fr,10*log10(Px),'LineWidth',2);
   ylabel('dB')
end
%title('estimated psd')
xlabel('Hz')
end






