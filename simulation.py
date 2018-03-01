from os import listdir
from os.path import isfile, join

from sklearn import svm
from sklearn import preprocessing

import watch_sensor

clf = svm.SVC(probability=True)
def init():
    train_x = []
    train_y = []

    valid_x = []
    valid_y = []

    for z in range(2):
        mypath = 'SensorLog/sb' + str(z+1)
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        pre_data = {}

        for gesture in ['pinch', 'wave', 'rub']:
            windows = {
                    1: [], #acc
                    4: [], #gyr
                    10 : [] #lin
                    }

            target_list = []
            for k in range(3):
                target_list.append(gesture+str(k+1))
            for j, target in enumerate(target_list):
                for onlyfile in onlyfiles:
                    if onlyfile.split('_')[0] != target:
                        continue
                    with open(mypath + '/' + onlyfile) as f_r:
                        data_type = 0
                        data_type_str = onlyfile.split('.')[0].split('_')[1]
                        if data_type_str == 'accel':
                            data_type = 1
                        elif data_type_str == 'gyro':
                            data_type = 4
                        elif data_type_str == 'linear':
                            data_type = 10

                        window = []
                        lines = f_r.read().splitlines()
                        for i, line in enumerate(lines):
                            if i == 0:
                                continue
                            data_list = line.split(',')
                            data_dict = {
                                    'time': int(data_list[0].split('.')[0]),
                                    'x': float(data_list[1]),
                                    'y': float(data_list[2]),
                                    'z': float(data_list[3]),
                                    }
                            if 1000 <= data_dict['time']:
                                if len(window) != 0 and (data_dict['time'] - window[0]['time']) > 1000:
                                    windows[data_type].append(window)
                                    if len(windows[data_type]) == 20 * (j + 1):
                                        break
                                    window = [data_dict]
                                window.append(data_dict)
            pre_data[gesture] = windows

        for gesture in ['pinch', 'wave', 'rub']:
            windows = pre_data[gesture]
            for i in range(len(windows[1])):
                data = {
                    1: windows[1][i],
                    4: windows[4][i],
                    10: windows[10][i]
                    }
                gesture_type = 0
                if gesture == 'pinch':
                    gesture_type = 1
                elif gesture == 'wave':
                    gesture_type = 4
                elif gesture == 'rub':
                    gesture_type = 2
                feature = watch_sensor.feature_generate(data)

                if z == 0:
                    train_x.append(preprocessing.scale(feature))
                    train_y.append(gesture_type)
                elif z == 1:
                    valid_x.append(preprocessing.scale(feature))
                    valid_y.append(gesture_type)

    clf.fit(train_x + valid_x, train_y + valid_y)

    '''
    pinch_pinch = 0
    pinch_wave = 0
    pinch_rub = 0
    wave_pinch = 0
    wave_wave = 0
    wave_rub = 0
    rub_pinch = 0
    rub_wave = 0
    rub_rub = 0
    for x, y in zip(valid_x, valid_y):
        predicted = clf.predict([x])[0]
        if y == 1 and predicted == 1:
            pinch_pinch += 1
        elif y == 1 and predicted == 4:
            pinch_wave += 1
        elif y == 1 and predicted == 2:
            pinch_rub += 1
        elif y == 4 and predicted == 4:
            wave_wave += 1
        elif y == 4 and predicted == 1:
            wave_pinch += 1
        elif y == 4 and predicted == 2:
            wave_rub += 1
        elif y == 2 and predicted == 2:
            rub_rub += 1
        elif y == 2 and predicted == 1:
            rub_pinch += 1
        elif y == 2 and predicted == 4:
            rub_wave += 1
    print pinch_pinch, pinch_wave, pinch_rub
    print wave_pinch, wave_wave, wave_rub
    print rub_pinch, rub_wave, rub_rub
    '''

def predict(features):
    return clf.predict([preprocessing.scale(features)])[0]

def predict_prob(features):
    return clf.predict_proba([preprocessing.scale(features)])[0]

#init()
