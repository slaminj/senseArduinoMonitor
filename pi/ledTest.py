import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
ledPinCharge = 6
ledPinDischarge = 5
GPIO.setup(ledPinCharge, GPIO.OUT)
GPIO.setup(ledPinDischarge, GPIO.OUT)

def chargeLED(on):
    if (on):
        #print("chargeLED turning on.")
        GPIO.output(ledPinCharge, GPIO.LOW)
    else:
        #print("chargeLED turning off.")
        GPIO.output(ledPinCharge, GPIO.HIGH)
def dischargeLED(on):
    if (on):
        print("dischargeLED turning on.")
        GPIO.output(ledPinDischarge, GPIO.HIGH)
    else:
        print("dischargeLED turning off.")
        GPIO.output(ledPinDischarge, GPIO.LOW)

chargeLED(False)
dischargeLED(False)
for i in range(10):
    print(i, "on")
    chargeLED(True)
    time.sleep(1)
    print(i, "off")
    chargeLED(False)
    time.sleep(5)

# for i in range(2):
#     dischargeLED(True)
#     time.sleep(2)
#     dischargeLED(False)
#     time.sleep(1)

#GPIO.cleanup()