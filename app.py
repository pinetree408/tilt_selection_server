# -*- coding: utf-8 -*-
from threading import Lock
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

import sys
import os
import json
import time
import watch_sensor
import watch_svm
import time

current_milli_time = lambda: int(round(time.time() * 1000))

app = Flask(__name__)
app.secret_key = "secret"
app.debug = False
socketio = SocketIO(app, async_mode=None)

thread_lock = Lock()

watch_svm.init()

windows = {
        1: [], #acc
        4: [], #gyr
        10 : [] #lin
        }

start_time = None

def background_thread(data):
    global windows, start_time
    prepared = watch_sensor.data_parser(data, windows)
    if prepared:
        if start_time is None:
            start_time = current_milli_time()
        else:
            if current_milli_time() - start_time > 200:
                start_time = current_milli_time()
                result = watch_sensor.feature_generate(windows)
                predicted = watch_svm.predict(result)
                gesture = ""
                if predicted == 1:
                    gesture = "pinch"
                elif predicted == 2:
                    gesture = "rub"
                elif predicted == 3:
                    gesture = "squeeze"
                elif predicted == 4:
                    gesture = "wave"
                print watch_svm.predict_prob(result), gesture
                '''
                socketio.emit("response", {
                    'type': 'Server event',
                    'data': gesture,
                    },
                    namespace='/mynamespace',
                    broadcast=True)
                '''

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.on('connect', namespace='/mynamespace')
def connect():
    emit("response", {
        'type': 'System',
        'data': 'Connected'
    })

@socketio.on('disconnet', namespace='/mynamespace')
def disconnect():
    print "Disconnect"

@socketio.on("request", namespace='/mynamespace')
def request(message):
    with thread_lock:
        thread = socketio.start_background_task(background_thread, message)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
