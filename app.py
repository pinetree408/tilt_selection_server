# -*- coding: utf-8 -*-
from threading import Lock
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

import time
import watch_sensor
import svm


def current_milli_time():
    return int(round(time.time() * 1000))


app = Flask(__name__)
app.secret_key = "secret"
app.debug = False
socketio = SocketIO(app, async_mode=None)

thread_lock = Lock()

svm.init()

windows = {
    1: [],  # acc
    4: [],  # gyr
    10: []  # lin
}

start_time = None


def background_thread(sens_type, sens_time, sens_x, sens_y, sens_z):
    global windows, start_time, gesture_window
    watch_sensor.data_parser(
        sens_type, sens_time, sens_x, sens_y, sens_z, windows)
    prepared = watch_sensor.check_prepared(windows)
    if prepared:
        if start_time is None:
            start_time = current_milli_time()
        else:
            if current_milli_time() - start_time > 20:
                start_time = current_milli_time()
                feature = watch_sensor.feature_generate(windows)
                predicted = svm.predict(feature)
                socketio.emit("response", {
                    'type': 'Server event',
                    'data': predicted,
                    },
                    namespace='/mynamespace',
                    broadcast=True)


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('connect', namespace='/mynamespace')
def connect():
    print "Connect"
    emit("response", {
        'type': 'System',
        'data': 'Connected'
    })


@socketio.on('disconnect', namespace='/mynamespace')
def disconnect():
    print "Disconnect"


@socketio.on("request", namespace='/mynamespace')
def request(sens_type, sens_time, sens_x, sens_y, sens_z):
    with thread_lock:
        socketio.start_background_task(
            background_thread, sens_type, sens_time, sens_x, sens_y, sens_z)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
