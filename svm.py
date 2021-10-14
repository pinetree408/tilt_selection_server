from os import listdir
from os.path import isfile, join

from sklearn import svm
from sklearn import preprocessing

import watch_sensor
import config

clf = svm.SVC(probability=True)


def init(debug=False):
    train_x = []
    train_y = []

    valid_x = []
    valid_y = []

    for z in range(2):
        mypath = 'SensorLog/' + config.USER_DIR + '/' + config.USER_NAME + '_' + str(z+1)
        onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

        pre_data = {}

        for gesture in ['pinch', 'wave', 'keep', 'tilt']:
            windows = {
                1: [],  # acc
                4: [],  # gyr
                10: []  # lin
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
                                    'time': float(data_list[0]),
                                    'x': float(data_list[1]),
                                    'y': float(data_list[2]),
                                    'z': float(data_list[3]),
                                    }
                            data_time = data_dict['time']
                            if 1000 < data_time:
                                if len(window) != 0 and \
                                        data_time - window[0]['time'] >= 1000:
                                    windows[data_type].append(window)
                                    if len(windows[data_type]) == 22 * (j + 1):
                                        break
                                    window = [data_dict]
                                window.append(data_dict)
            pre_data[gesture] = windows

        for gesture in ['pinch', 'wave', 'keep', 'tilt']:
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
                    gesture_type = 2
                elif gesture == 'keep':
                    gesture_type = 3
                elif gesture == 'tilt':
                    gesture_type = 4

                feature = watch_sensor.feature_generate(data)

                if debug == True:
                    if z == 0:
                        train_x.append(preprocessing.scale(feature))
                        train_y.append(gesture_type)
                    elif z == 1:
                        valid_x.append(preprocessing.scale(feature))
                        valid_y.append(gesture_type)
                else:
                    train_x.append(preprocessing.scale(feature))
                    train_y.append(gesture_type)

    clf.fit(train_x, train_y)
    if debug == True:
        gesture_set = [1, 2, 3, 4]
        result = [0] * (4 * 4)
        for x, y in zip(valid_x, valid_y):
            predicted = clf.predict([x])[0]
            for g_i in gesture_set:
                for g_j in gesture_set:
                    if g_i == y and predicted == g_j:
                        result[(g_i - 1)*len(gesture_set) + (g_j - 1)] += 1

        for i in range(len(gesture_set)):
            print(result[i*len(gesture_set) : (i+1)*len(gesture_set)])


def predict(features):
    return clf.predict([preprocessing.scale(features)])[0]


def predict_prob(features):
    return clf.predict_proba([preprocessing.scale(features)])[0]

if __name__ == '__main__':
    init(debug=True)
