import os
import atexit
import time
raspberry_pi = os.uname()[4][:3] == 'arm'

print('PI:', raspberry_pi)
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, send

if raspberry_pi:
    from pi import setServoPulse, setMotorSpeed
    from adafruit.Adafruit_Servo_Driver import PWM
    from adafruit.Adafruit_MotorHAT import Adafruit_MotorHAT
    # Adafruit_DCMotor

'''
  TODO:
    change print's to debug

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

app.horizontal_offset = 125
app.vertical_offset = 125

io = SocketIO(app)

# init x,y,z acceleration -
ax = 0
ay = 0
az = 0
ra = 0
rb = 0
rg = 0

# compass data
cGamma = 0
cBeta = 0
cAlpha = 0
cHeading = 0
cAccuracy = 0

# Initialise the PWM device using the default address
freq = 60
if raspberry_pi:
    pwm = PWM(0x40)
    # Note if you'd like more debug output you can instead run:
    # pwm = PWM(0x40, debug=True)
    # pwm.setPWMFreq(60)                        # Set frequency to 60 Hz
    pwm.setPWMFreq(freq)

    # motor hat
    # create a default object,
    mh = Adafruit_MotorHAT(addr=0x61)


def turnOffMotors():
    mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

#Motors!
m1 = mh.getMotor(1)
m2 = mh.getMotor(2)
m3 = mh.getMotor(3)
m4 = mh.getMotor(4)

#Turn off motors on exit
atexit.register(turnOffMotors)


#### Motor Test

TEST = False
if TEST:
    while (True):
        print ("Forward! ")
        m1.run(Adafruit_MotorHAT.FORWARD)
        m2.run(Adafruit_MotorHAT.FORWARD)
        m3.run(Adafruit_MotorHAT.FORWARD)
        m4.run(Adafruit_MotorHAT.FORWARD)
        m1.setSpeed(100)
        m2.setSpeed(100)
        m3.setSpeed(100)
        m4.setSpeed(100)
        time.sleep(1)

        print ("Stop")
        m1.setSpeed(00)
        m2.setSpeed(00)
        m3.setSpeed(00)
        m4.setSpeed(00)
        time.sleep(1)

        print ("Backward! ")
        m1.run(Adafruit_MotorHAT.BACKWARD)
        m2.run(Adafruit_MotorHAT.BACKWARD)
        m3.run(Adafruit_MotorHAT.BACKWARD)
        m4.run(Adafruit_MotorHAT.BACKWARD)
        m1.setSpeed(100)
        m2.setSpeed(100)
        m3.setSpeed(100)
        m4.setSpeed(100)
        time.sleep(1)


        print ("Stop")
        m1.setSpeed(00)
        m2.setSpeed(00)
        m3.setSpeed(00)
        m4.setSpeed(00)
        time.sleep(1)


        print ("TURN!")
        m1.run(Adafruit_MotorHAT.FORWARD)
        m2.run(Adafruit_MotorHAT.FORWARD)
        m3.run(Adafruit_MotorHAT.BACKWARD)
        m4.run(Adafruit_MotorHAT.BACKWARD)
        m1.setSpeed(100)
        m2.setSpeed(100)
        m3.setSpeed(100)
        m4.setSpeed(100)
        time.sleep(2.3)

        print ("Stop")
        m1.setSpeed(00)
        m2.setSpeed(00)
        m3.setSpeed(00)
        m4.setSpeed(00)
        time.sleep(1)


        print ("Release")
        m1.run(Adafruit_MotorHAT.RELEASE)
        m2.run(Adafruit_MotorHAT.RELEASE)
        m3.run(Adafruit_MotorHAT.RELEASE)
        m4.run(Adafruit_MotorHAT.RELEASE)
        time.sleep(1.0)


# Scale value N,  from one range to new range.
# eg. from  -1 to 1   --> -255 to 255
def renormalize(n, range1, range2):
    delta1 = range1[1] - range1[0]
    delta2 = range2[1] - range2[0]
    return (delta2 * (n - range1[0]) / delta1) + range2[0]


# set speed (and direction) of left motors
def set_left_speed(speed):
    m1.run(Adafruit_MotorHAT.FORWARD)
    m2.run(Adafruit_MotorHAT.FORWARD)
    print ('left speed:', speed)

    if speed < 0:
        speed = abs(speed)
        m1.run(Adafruit_MotorHAT.BACKWARD)
        m2.run(Adafruit_MotorHAT.BACKWARD)
    m1.setSpeed(speed)
    m2.setSpeed(speed)
# set speed (and direction) of right motors

def set_right_speed(speed):
    m3.run(Adafruit_MotorHAT.FORWARD)
    m4.run(Adafruit_MotorHAT.FORWARD)
    print('right speed:', speed)

    if speed < 0:
        speed = abs(speed)
        m3.run(Adafruit_MotorHAT.BACKWARD)
        m4.run(Adafruit_MotorHAT.BACKWARD)
    m3.setSpeed(speed)
    m4.setSpeed(speed)

@io.on('connect')
def ws_conn():
    print('hello connect')


# take the joystick input and scale it to a pulse width out of 4096
def scale_input(joy_input, c_offset=0):
    # c_offset param in the 0 - 1 range.. and can be negative
    #debug offset
    #print("--------------------------------", c_offset)
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


@app.route('/')
def hello_world():
    return render_template('index.jade', title='Rover-Pi')


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
    if amount:
        app.vertical_offset += amount * 5
        if app.vertical_offset > 255:
            app.vertical_offset = 255
        if app.vertical_offset < 0:
            app.vertical_offset = 0
        print(app.vertical_offset)


@io.on('horizontal offset', namespace='/rover')
def increase_horizontal(amount):
    if amount:
        print('amount:', amount)
        app.horizontal_offset += float(amount) * 5
        if app.horizontal_offset > 255:
            app.horizontal_offset = 255
        if app.horizontal_offset < 0:
            app.horizontal_offset = 0
        print(app.horizontal_offset)


@io.on('gamepadUpdate', namespace='/rover')
def update_gamepad(data):
    # recommended for auto-disabling motors on shutdown!
    print('JOYSTICK DATA:', data)  # gamepad data "x1=n;y1=n;x2=n;y2=n;x3=n;..."
    axis = data.split(';')

    # no x offset
    x_offset = 0
    # tilt y axis up just a tad
    y_offset = 0
    # -1.8 for toy

    #bkd - horizontal offset
    app.horizontal_offset = 0
    app.vertical_offset = -0.1
    # joystick 1
    x0 = scale_input(float(axis[0].split('=')[1]), app.horizontal_offset)
    # flip y axis
    y0 = scale_input(-1 * float(axis[1].split('=')[1]), app.vertical_offset)

    # joystick 1
    x0 = scale_input(float(axis[0].split('=')[1]), app.horizontal_offset)
    # flip y axis
    y0 = scale_input(-1 * float(axis[1].split('=')[1]), app.vertical_offset)

    # #joystick 2
    # x1 = scale_input(float(axis[2].split('=')[1]),app.horizontal_offset)
    # #flip y axis
    # y1 = scale_input(-1.0 * float(axis[3].split('=')[1]),app.vertical_offset)


    motor_input_range = (-1, 1)
    # motor_output_range = (-255, 255)

    #think we're at low voltage for motors..
    # lower speed values don't actually  move motors, so scale everything up
    # don't know what happens when we're out of range, but we can fix that
    motor_output_range = (-400,400)

    # joystick 2 ---- Driving !
    x1_output = float(axis[2].split('=')[1])
    y1_output = -1 * float(axis[3].split('=')[1])


    x1 = renormalize(float(axis[2].split('=')[1]), motor_input_range, motor_output_range)
    y1 = renormalize(-1 * float(axis[3].split('=')[1]), motor_input_range, motor_output_range)

    x1 = int(x1)
    y1 = int(y1)

    #start out both motors forward
    left_speed = y1
    right_speed =y1

    #turning

    # x1 can be less than 1, lets min that at 1 to keep things sane
    #  the last multiplier is to lessen the effect of the x axis
    #  eg. 0.1 - 0.9 (we are making X smaller, which has less of an effect on the div to follow
    #     put another way.. the smaller the x factor the less effect it has on turning
    x_factor = max(1, abs(x1 * 0.01) )
    slower_wheel_speed = int(y1/x_factor)

    if x1 > 0:
        right_speed = slower_wheel_speed
    if x1 < 0:
        left_speed = slower_wheel_speed


    ## spin
    if y1 == 0:
        right_speed =  -x1
        left_speed  = x1

    # if standing still,  turn off motors
    if (y1 == 0) and (x1 == 0):
        turnOffMotors()
    else:
        #move motors
        set_left_speed(left_speed)
        set_right_speed(right_speed)

    print('x0:', x1, ' y0:', y0, ' x1:', x1, ' y1:', y1)

    # pwm.setPWM(0, 0, y1)

    # pan and tilt 1
    if raspberry_pi:
        print ('PANTILT:',y0,":",x0)
        pwm.setPWM(0, 0, y0)
        pwm.setPWM(1, 0, x0)


        # pan and tilt 2
        # pwm.setPWM(2, 0, x1)
        # pwm.setPWM(3, 0, y1)


@io.on('compassUpdate')
def update_compass(data):
    cdata = data.split(';')
    cGamma = cdata[0].split('=')[1]
    cBeta = cdata[1].split('=')[1]
    cAlpha = cdata[2].split('=')[1]
    cHeading = cdata[3].split('=')[1]
    cAccuracy = cdata[4].split('=')[1]

    # print ('compass:',cGamma, cBeta, cAlpha, cHeading, cAccuracy)
    print('Heading:', cHeading)

    y2 = scale_heading(cHeading)
   # pwm.setPWM(4, 0, y2)


@io.on('gyroUpdate')
def update_gyro(data):
    # print("gyrodata:", data)
    axis = data.split(';')
    # split into pairs, grab out the data from the pair
    ax = axis[0].split('=')[1]
    ay = axis[1].split('=')[1]
    az = axis[2].split('=')[1]
    ra = axis[3].split('=')[1]
    rb = axis[4].split('=')[1]
    rg = axis[5].split('=')[1]
    # print ('orientation:',ax,ay,az,ra,rb,rg)


if __name__ == '__main__':
    app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
    io.run(app, host='0.0.0.0')
