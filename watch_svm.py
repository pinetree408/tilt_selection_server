from os import listdir
from os.path import isfile, join
from sklearn import svm
from sklearn import preprocessing

clf = svm.SVC(probability=True)


def init():
    mypath = 'Sorted_squeeze_added'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for onlyfile in onlyfiles[:1]:
        with open(mypath + '/' + onlyfile, 'r') as f_r:
            lines = f_r.read().splitlines()
            train_x = []
            train_y = []
            valid_x = []
            valid_y = []
            for line in lines:
                gesture = line.split(', ')[0]
                if gesture == "pinch":
                    gesture = 1
                elif gesture == "rub":
                    gesture = 2
                elif gesture == "squeeze":
                    gesture = 3
                elif gesture == "wave":
                    gesture = 4
                if not (gesture == 1 or gesture == 4):
                    continue
                day = line.split(', ')[2]
                features = line.split(', ')[4:]
                features = [float(feature) for feature in features]
                if day == '1':
                    train_x.append(features)
                    train_y.append(gesture)
                elif day == '2':
                    valid_x.append(features)
                    valid_y.append(gesture)

            train_x = preprocessing.scale(train_x)
            valid_x = preprocessing.scale(valid_x)
            clf.fit(train_x, train_y)
            '''
            pinch_pinch = 0
            pinch_wave = 0
            wave_pinch = 0
            wave_wave = 0
            for x, y in zip(valid_x, valid_y):
                predicted = clf.predict([x])[0]
                if y == 1 and predicted == 1:
                    pinch_pinch += 1
                elif y == 1 and predicted == 4:
                    pinch_wave += 1
                elif y == 4 and predicted == 4:
                    wave_wave += 1
                elif y == 4 and predicted == 1:
                    wave_pinch += 1
            print pinch_pinch, pinch_wave
            print wave_pinch, wave_wave
            '''


def predict(features):
    return clf.predict([preprocessing.scale(features)])[0]


def predict_prob(features):
    return clf.predict_proba([preprocessing.scale(features)])[0]
