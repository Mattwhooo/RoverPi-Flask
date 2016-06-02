import os

raspberry_pi = os.uname()[4][:3] == 'arm'

from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, send
if raspberry_pi:
    from pi import setServoPulse, setMotorSpeed

users = {}
app = Flask(__name__)
io = SocketIO(app)

app.horizontal_offset = 0
app.vertical_offset = 0

@app.route('/')
def hello_world():
    return render_template('index.jade', title = 'Rover-Pi')

@io.on('broadcast user', namespace='/rover')
def test_message(message):
    users[request.sid] = message
    emit('newUser', message, broadcast=True)

@io.on('broadcast remove controller', namespace='/rover')
def test_message():
    emit('removeController', users[request.sid], broadcast=True)

@io.on('broadcast controller', namespace='/rover')
def test_message():
    emit('newController', users[request.sid], broadcast=True)

@io.on('connect', namespace='/rover')
def test_connect():
    print('client connected')
    emit('who am i', {'data': 'Connected'})

@io.on('disconnect', namespace='/rover')
def test_disconnect():
    print('Client disconnected')
    emit('removeUser', users[request.sid], broadcast=True)

@io.on('vertical offset', namespace='/rover')
def increase_vertical(amount):
    app.vertical_offset += amount
    print(app.vertical_offset)

@io.on('horizontal offset', namespace='/rover')
def increase_vertical(amount):
    app.horizontal_offset += amount
    print(app.horizontal_offset)

@io.on('gamepadUpdate', namespace='/rover')
def update_gamepad(data):
   print(data)
   axis = data.split(';')
   for a in axis:
       if a != '':
           axis_data = a.split('=')
           if axis_data[0] == '2' or axis_data[0] == '3':
                if raspberry_pi:
                    setServoPulse(int(axis_data[0]), float(axis_data[1]))
           else:
                if raspberry_pi:
                    setMotorSpeed(int(axis_data[0]), float(axis_data[1]))

if __name__ == '__main__':
    app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

    io.run(app, host='0.0.0.0')