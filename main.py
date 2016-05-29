from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, send
from pi import setServoPulse, setMotorSpeed

users = {}
app = Flask(__name__)
io = SocketIO(app)

@app.route('/')
def hello_world():
    # io.emit('newUser', 'Test User?')
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

@io.on('gamepadUpdate', namespace='/rover')
def update_gamepad(data):
   print(data)
   axis = data.split(';')
   for a in axis:
       if a != '':
           axis_data = a.split('=')
           if axis_data[0] == '2' or axis_data[0] == '3':
             setServoPulse(int(axis_data[0]), float(axis_data[1]))
           else:
             setMotorSpeed(int(axis_data[0]), float(axis_data[1]))

if __name__ == '__main__':
    app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

    io.run(app)