# -*- coding: utf-8 -*-
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

import os
import json
import time

app = Flask(__name__)
app.secret_key = "secret"
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

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
    print message
    emit("response", {
        'type': 'Sentence',
        'data': message['data'],
    }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
