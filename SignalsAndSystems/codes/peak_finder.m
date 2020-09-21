 function peak = peak_finder(address)
%     a1 = 'D:\semester5\SignalsAndSystems\Project\Bonus_Project\voices\v';
%     a2 = strcat(a1,int2str(voice_number));
%     address = strcat(a2,'.mp3');
    [x,fs] = audioread(address); %read the audio file
    y = fft(x); % calculate the Fourier transform
    power_specturm_density = abs(y).^2; %calculate the power spectrum
    f = linspace(0, 1000, fs/2 + 1);
    [~, peak_x] = max(power_specturm_density);
    peak = f(peak_x); %find the peak
    fprintf('%f \n',peak);
end