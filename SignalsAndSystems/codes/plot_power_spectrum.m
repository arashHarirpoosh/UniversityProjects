function plot_power_spectrum(voice_number) 
     a1 = 'D:\semester5\SignalsAndSystems\Project\Bonus_Project\voices\v';
     a2 = strcat(a1,int2str(voice_number));
     address = strcat(a2,'.mp3');
     [x,fs] = audioread(address); %read the audio file    
     n = length(x);       % original sample length
     %n = pow2(nextpow2(m));  % transform length
     y = fft(x, n); % calculate the Fourier transform
     f = linspace(0,1000,fs/2+1);
     power = abs(y).^2/10.^6; %calculate powerspectrum
     plot(f,power(1:length(f)));
     %[~, peak_x] = max(power);
     %ff = f(peak_x);
    %title(sprintf("%f", ff));
     title('power spectrum');
     xlabel('Frequency')
     ylabel('Power')
     h = figure(1);
     file_name = strcat('v',int2str(voice_number),'.png');
     saveas(h,fullfile('D:\semester5\SignalsAndSystems\Project\Bonus_Project',file_name));% save the plot result
end
