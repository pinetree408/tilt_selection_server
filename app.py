# -*- coding: utf-8 -*-
from threading import Lock
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

import time
import watch_sensor
import svm
import csv

def current_milli_time():
    return int(round(time.time() * 1000))


app = Flask(__name__)
app.secret_key = "secret"
app.debug = False
socketio = SocketIO(app, async_mode=None)

thread_lock = Lock()

svm.init()
print "svm -- initialize"

windows = {
    1: [],  # acc
    4: [],  # gyr
    10: []  # lin
}

start_time = None
predicted_window = []
pre_predicted_gesture = -1

now_target = ''
f = None
csv_wr = None


def background_thread(sens_type, sens_time, sens_x, sens_y, sens_z):
    global windows, start_time, predicted_window, pre_predicted_gesture, csv_wr
    watch_sensor.data_parser(
        sens_type, sens_time, sens_x, sens_y, sens_z, windows)
    prepared = watch_sensor.check_prepared(windows)
    if prepared:
        if start_time is None:
            start_time = current_milli_time()
        else:
            if current_milli_time() - start_time > 50:
                start_time = current_milli_time()
                feature = watch_sensor.feature_generate(windows)
                probs = list(svm.predict_prob(feature))
                max_prob = max(probs)
                predicted = [probs.index(max_prob), max_prob]
                if len(predicted_window) == 3:
                    if (predicted_window[0][0] == predicted_window[1][0]\
                            and predicted_window[1][0] == predicted_window[2][0]):
                        if (predicted_window[0][1] > 0.4\
                                and predicted_window[1][1] > 0.4
                                and predicted_window[2][1] > 0.4):
                            target = predicted_window[1][0] + 1
                            if (pre_predicted_gesture == 2) and target == 1:
                                target = 2
                            pre_predicted_gesture = target

                            if csv_wr != None:
                                csv_wr.writerow([now_index, now_target, target])

                            socketio.emit("response", {
                                'type': 'Predicted',
                                'data': target,
                                },
                                namespace='/mynamespace',
                                broadcast=True)
                    predicted_window.pop(0)
                predicted_window.append(predicted)


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('connect', namespace='/mynamespace')
def connect():
    print "Connect"
    emit("response", {
        'type': 'System',
        'data': 'Connected',
    })


@socketio.on('disconnect', namespace='/mynamespace')
def disconnect():
    print "Disconnect"
    emit("response", {
        'type': 'System',
        'data': 'Disconnected'
    })

@socketio.on('start', namespace='/mynamespace')
def start():
    print "Task Start"
    global f, csv_wr
    f = open('sb_2.csv', 'wb')
    csv_wr = csv.writer(f)

@socketio.on('intask', namespace='/mynamespace')
def intask(index, target):
    global now_index, now_target
    now_index = index
    now_target = target
    print now_index, now_target


@socketio.on('done', namespace='/mynamespace')
def done():
    global f, csv_wr
    print "Task Done"
    f.close()
    f = None
    csv_wr = None

@socketio.on("request", namespace='/mynamespace')
def request(sens_type, sens_time, sens_x, sens_y, sens_z):
    with thread_lock:
        socketio.start_background_task(
            background_thread, sens_type, sens_time, sens_x, sens_y, sens_z)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
