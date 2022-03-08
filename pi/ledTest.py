import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
ledPinCharge = 11
ledPinDischarge = 12
GPIO.setup(ledPinCharge, GPIO.OUT)
GPIO.setup(ledPinDischarge, GPIO.OUT)

def chargeLED(on):
    if (on):
        print("chargeLED turning on.")
        GPIO.output(ledPinCharge, GPIO.HIGH)
    else:
        print("chargeLED turning off.")
        GPIO.output(ledPinCharge, GPIO.LOW)
def dischargeLED(on):
    if (on):
        print("dischargeLED turning on.")
        GPIO.output(ledPinDischarge, GPIO.HIGH)
    else:
        print("dischargeLED turning off.")
        GPIO.output(ledPinDischarge, GPIO.LOW)

for i in range(2):
    chargeLED(True)
    time.sleep(1)
    chargeLED(False)
    time.sleep(1)

for i in range(2):
    dischargeLED(True)
    time.sleep(1)
    dischargeLED(False)
    time.sleep(1)

GPIO.cleanup()