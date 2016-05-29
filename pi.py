#!/usr/bin/python
# from adafruit.Adafruit_Servo_Driver import PWM
# from adafruit.Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
import atexit
import time

# ===========================================================================
# Example Code
# ===========================================================================

# Initialise the PWM device using the default address
# pwm = PWM(0x60)
# Note if you'd like more debug output you can instead run:
#pwm = PWM(0x40, debug=True)

servoMin = 150  # Min pulse length out of 4096
servoMax = 600  # Max pulse length out of 4096

def setServoPulse(channel, pulse):
  pulse = (pulse + 1) / 2 #normalize pulse for 0..1 range
  pulse = (servoMax - servoMin) * pulse  + servoMin #set pulse in range of min..max
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 60 Hz
  pulseLength /= 4096                     # 12 bits of resolution
  pulse *= 1000
  pulse /= pulseLength
  # pwm.setPWM(channel, 0, pulse)

# pwm.setPWMFreq(60)                        # Set frequency to 60 Hz

# mh = Adafruit_MotorHAT(addr=0x61)

# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
  pass
	# mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
	# mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
	# mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
	# mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)

atexit.register(turnOffMotors)


def setMotorSpeed(motor, speed):

  # if speed < 0:
  #   direction = Adafruit_MotorHAT.BACKWARD
  # else:
  #   direction = Adafruit_MotorHAT.FORWARD

  speed *= 255
  speed = abs(speed)

  # myMotor = mh.getMotor(motor)
  #
  # myMotor.run(direction)
  # myMotor.setSpeed(speed)
  # myMotor.run(Adafruit_MotorHAT.RELEASE);
