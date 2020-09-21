function genderDetection(folder_address) 
    voice_folder = dir(fullfile(folder_address,'*.mp3')); % The folder in which the voice files has been saved
    fileID = fopen('D:\semester5\SignalsAndSystems\Project\Bonus_Project\gender_label.txt','w');
     for i = 1:length(voice_folder)
        peak = peak_finder(fullfile(folder_address,voice_folder(i).name)); %find the peak
        fileAddress = strsplit(fullfile(folder_address,voice_folder(i).name), '\');
        full_file_name = strsplit(fileAddress{7},'.');
        file_name = full_file_name{1};% find the name of the file
        fprintf('%s \n', file_name); 
        %if (peak <= 180 && peak >= 50)
        if (peak <= 165)
            label = strcat(file_name, ' male'); % detect the voice as male voice
        %elseif(peak >= 165 && peak <= 255)
        elseif(peak >= 165)
            label = strcat(file_name, ' female'); % detect the voice as female voice
        else 
            label = strcat(file_name, ' not detected');
        end
        fprintf(fileID, ' %s \n',label); % write the result in the file
    end
end
