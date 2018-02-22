from os import listdir
from os.path import isfile, join
from sklearn import svm
from sklearn import preprocessing

clf = svm.SVC()
def init():
    mypath = 'Sorted_squeeze_added'
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for onlyfile in onlyfiles[1:2]:
        with open(mypath + '/'+ onlyfile, 'r') as f_r:
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
                posture = line.split(', ')[1]
                day = line.split(', ')[2]
                window = line.split(', ')[3]
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

def predict(features):
    return clf.predict([preprocessing.scale(features)])[0]
