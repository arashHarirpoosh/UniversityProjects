function SpectralSubtraction(awgn_rate) 
[y,fs] = audioread('D:\semester5\SignalsAndSystems\Project\Bonus_Project\Test.wav');
%% Add noise
S = RandStream('mt19937ar','Seed',5489);
Noisesignal = awgn(y,awgn_rate,0,S); %noise2
%Noisesignal = awgn(y,awgn_rate,'measured'); %noise1

%% spectral substraction
gamma = 0.25;
omega = 0.75;
%gamma = 1;
%omega = 1;
% signal spectrum
spectrum_noisy_signal = fft(Noisesignal);
spectrum_noisy_signal_mag = abs(spectrum_noisy_signal);
phase_signal = angle(spectrum_noisy_signal);
%findNoise
noise_r = spectrum_noisy_signal_mag(1:8218);
Noise = mean(omega.*noise_r);
fprintf("%f\n", abs(Noise));
% subtract spectrum
subtracted_spectrum_mag = (spectrum_noisy_signal_mag.^gamma - omega.*Noise.^gamma).^(1/gamma);
subtracted_spectrum_mag(subtracted_spectrum_mag < 0) = 0.5;

 %recover original spectrum and signal
enhanced_spectrum = awgn_rate.*subtracted_spectrum_mag .* exp(1i*phase_signal);
original_signal = ifft(enhanced_spectrum);

figure;
 subplot(3,1,3);
 plot(real(original_signal));
 title("FilterdSound");
 subplot(3,1,2);
 plot(Noisesignal);
 title("NoiseSound");
 subplot(3,1,1);
 plot(y);
  title("originalSound");

sound(real(Noisesignal), fs);
pause(4);
sound(real(original_signal), fs);
filename = 'D:\semester5\SignalsAndSystems\Project\Bonus_Project\WT.wav';
audiowrite(filename,real(original_signal), fs);
end