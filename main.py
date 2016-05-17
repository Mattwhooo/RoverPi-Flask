from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit
from pi import setServoPulse, setMotorSpeed

'''
  Servo thinking
	Pulse width defines servo angle
	
	___|-|___ 
           1.5ms     is neutral

	___|---|___
	   2.0ms    from 1.0 to 2.0 usually yields about 90deg movement
	
	Neutral does not mean centered = for a 180deg servo neutral may be 100
	there is not standard corresponence between angle and pulse width
	you should calibrate it. 

	no max or min pulse width.. 
	the direction isn't standarized either. 
	typical pulse period is about 50hz, but it doesn't change position
	it's still the pulse width.. 
	it does give the upper limit of how quick you can send servo commands


	setPWM ( channel, start(out of 4095), end (out of 4095)
		the len of the pulse is predifined in freq -- eg, 60hz or 1000hz etc..
		this defined what the pulse inside that pulse looks like

		________________________+-------------+________________
		0                      2000           3000            4096

		eg:  setPWM(0,2000,3000)

'''
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
   
   setServoPulse(0, axis[2].split('=')[1])
   setServoPulse(1, axis[3].split('=')[1])
   for a in axis:
       if a != '':
           axis_data = a.split('=')
           if axis_data[0] == '2' or axis_data[0] == '3':
             setServoPulse(0,axis_data[0])
#             setServoPulse(1,axis_data[1])
	     #print('axis we are talking to: %s' % (a))
             print('set servo pulse channel %s value %s' % (axis_data[0], axis_data[1]))
           else:
             pass
#             setMotorSpeed(axis_data[0], axis_data[1])
if __name__ == '__main__':
    app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

    io.run(app, host='0.0.0.0')
