% Data category
participants = ["상윤", "선범", "영보"];
gestures = ["pinch", "wave"];
sensors = ["accel", "gyro", "linear"];
for idxP = 1:3
    for day = 1:2
        for idxG = 1:2
            for posture = 1:3
                for idxS = 1:3
                    % Load .csv log file
                    loadDir = participants(idxP) + string(day) + '\' + gestures(idxG) + string(posture) + "_" + sensors(idxS) + '.csv'
                    file = csvread(loadDir, 1, 0);

                    % Interpolated & Calculated data storage
                    interpResult = zeros(1+ 50 * 20, 8);

                    for i=1:size(interpResult, 1)
                        % Time step: 20ms
                        time = (i - 1) * 20;
                        interpResult(i, 1) = time;
                        for j=1:size(file, 1)
                            if(file(j,1) > time + 1000)
                                break;
                            end
                        end

                        % x, y, z interpolation
                        slope = (file(j, [2:4]) - file(j-1, [2:4])) / (file(j,1) - file(j-1, 1));
                        interpResult(i, [2:4]) = slope * (time + 1000) + file(j, [2:4]) - slope * file(j,1);
                        
                        % m, xy, yz, xz calculation
                        x = interpResult(i, 2);
                        y = interpResult(i, 3);
                        z = interpResult(i, 4);
                        m = sqrt(x^2 + y^2 + z^2);
                        xy = sqrt(x^2 + y^2);
                        yz = sqrt(y^2 + z^2);
                        xz = sqrt(x^2 + z^2);
                        interpResult(i, 5:8) = [m xy yz xz];
                    end
                    
                    saveDir = 'D:\Onedrive\HCIL\차세정 과제\Serendipity Reimplementation\Interpolated\' + participants(idxP) + string(day)+ '\' + gestures(idxG) + string(posture) + "_" + sensors(idxS) + '.csv'
                    csvwrite(saveDir, interpResult);
                end
            end
        end
    end
end

