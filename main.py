import os

raspberry_pi = os.uname()[4][:3] == 'arm'

from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, send

if raspberry_pi:
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
users = {}
app = Flask(__name__)
io = SocketIO(app)

#init x,y,z acceleration -
ax = 0
ay = 0
az = 0
ra = 0
rb = 0
rg = 0

#compass data
cGamma = 0
cBeta  = 0
cAlpha = 0
cHeading = 0
cAccuracy = 0

# Initialise the PWM device using the default address
freq = 60
if raspberry_pi:
    pwm = PWM(0x40)
    # Note if you'd like more debug output you can instead run:
    #pwm = PWM(0x40, debug=True)
    #pwm.setPWMFreq(60)                        # Set frequency to 60 Hz
    pwm.setPWMFreq(freq)


def renormalize(n, range1, range2):
    delta1 = range1[1] - range1[0]
    delta2 = range2[1] - range2[0]
    return (delta2 * (n - range1[0]) / delta1) + range2[0]

@io.on('connect')
def ws_conn():
    print('hello connect')


# take the joystick input and scale it to a pulse width out of 4096
def scale_input(joy_input, c_offset = 0):
    # c_offset param in the 0 - 1 range.. and can be negative
    print ("--------------------------------",c_offset)
    # offset the range(-0.5 to 0.5), mult by servorange add min
    joy_input += 0.5
    # 450 - scaling from  0 - 1, to something out of 4096
    # the usable range for our servo is a pulse between 200 and 632
    scaled = joy_input * 450 * freq / 60  # account for frequency
    center_offset = freq * c_offset
    value = int(scaled + (150 * freq / 60) + center_offset)

    # limit min and max for servo position.
    # discovered these experimentally -
    value = max(value, int(200 * freq / 60))  # at 150Hz- 500 pulse width seems min
    value = min(value, int(632 * freq / 60))  # at 150Hz- 1580 pulse width seems max

    return value


def scale_heading(cHeading):
    # offset the range(-360 to 360), mult by servorange add min
    heading = 0.0
    heading = float(cHeading)
    heading += 360
    # 450 - scaling from  0 - 1, to something out of 4096
    # the usable range for our servo is a pulse between 200 and 632
    scaled = heading * 0.8 * freq / 60  # account for frequency
    center_offset = freq * 0.0
    value = int(scaled + (150 * freq / 60) + center_offset)

    # limit min and max for servo position.
    # discovered these experimentally -
    value = max(value, int(200 * freq / 60))  # at 150Hz- 500 pulse width seems min
    value = min(value, int(632 * freq / 60))  # at 150Hz- 1580 pulse width seems max

    return value

app.horizontal_offset = 125
app.vertical_offset = 125


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
    app.vertical_offset += amount * 5
    if app.vertical_offset > 255:
        app.vertical_offset = 255
    if app.vertical_offset < 0:
        app.vertical_offset = 0
    print(app.vertical_offset)

@io.on('horizontal offset', namespace='/rover')
def increase_horizontal(amount):
    app.horizontal_offset += amount * 5
    if app.horizontal_offset > 255:
        app.horizontal_offset = 255
    if app.horizontal_offset < 0:
        app.horizontal_offset = 0
    print(app.horizontal_offset)

@io.on('gamepadUpdate', namespace='/rover')
def update_gamepad(data):
   print('JOYSTICK DATA:',data)
   #gamepad data "x1=n;y1=n;x2=n;y2=n;x3=n;..."
   axis = data.split(';')

   #no x offset
   x_offset = 0
   # tilt y axis up just a tad
   y_offset = 0
  # -1.8 for toy

   #joystick 1
   x0 = scale_input(float(axis[0].split('=')[1]), app.horizontal_offset)
   # flip y axis
   y0 = scale_input(-1 * float(axis[1].split('=')[1]), app.vertical_offset)

   #joystick 2
   x1 = scale_input(float(axis[2].split('=')[1]),app.horizontal_offset)
   #flip y axis
   y1 = scale_input(-1.0 * float(axis[3].split('=')[1]),app.vertical_offset)

   print ('x0:',x1,' y0:',y0,' x1:',x1,' y1:',y1)

   #pwm.setPWM(0, 0, y1)

   #pan and tilt 1
   if raspberry_pi:
       pwm.setPWM(0, 0, y0)
       pwm.setPWM(1, 0, x0)


       #pan and tilt 2
       pwm.setPWM(2, 0, x1)
       pwm.setPWM(3, 0, y1)

@io.on('compassUpdate')
def update_compass(data):
    cdata = data.split(';')
    cGamma = cdata[0].split('=')[1]
    cBeta  = cdata[1].split('=')[1]
    cAlpha = cdata[2].split('=')[1]
    cHeading = cdata[3].split('=')[1]
    cAccuracy = cdata[4].split('=')[1]

    #print ('compass:',cGamma, cBeta, cAlpha, cHeading, cAccuracy)
    print ('Heading:',cHeading)

    y2 = scale_heading(cHeading)
    pwm.setPWM(4,0,y2)

@io.on('gyroUpdate')
def update_gyro(data):
   #print("gyrodata:", data)
   axis = data.split(';')
   #split into pairs, grab out the data from the pair
   ax = axis[0].split('=')[1]
   ay = axis[1].split('=')[1]
   az = axis[2].split('=')[1]
   ra = axis[3].split('=')[1]
   rb = axis[4].split('=')[1]
   rg = axis[5].split('=')[1]
   #print ('orientation:',ax,ay,az,ra,rb,rg)

if __name__ == '__main__':
    app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
    io.run(app, host='0.0.0.0')
