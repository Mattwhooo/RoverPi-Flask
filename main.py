from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit
from pi import setServoPulse, setMotorSpeed

app = Flask(__name__)
io = SocketIO(app)

@app.route('/')
def hello_world():
    return render_template('index.jade', title = 'Rover-Pi')

@io.on('connect')
def ws_conn():
    print('hello connect')

@io.on('gamepadUpdate')
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