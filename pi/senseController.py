from secrets import SENSE_PASS, SENSE_USER
from sense_energy  import Senseable
from time import time, gmtime, strftime
import logging
logging.basicConfig(filename='output.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
ledPinCharge = 11
ledPinDischarge = 12
GPIO.setup(ledPinCharge, GPIO.OUT)
GPIO.setup(ledPinDischarge, GPIO.OUT)

sense = Senseable()
sense.authenticate(SENSE_USER, SENSE_PASS)

class senseController:

    pastPower= 0
    pastSolar= 0
    updateInterval = 3
    lastCall = 0
    
    chargeW = 400
    charging = False
    
    def __init__(self):
        self.lastCall = time()

    def webSocketCallback(self):
        currPower = int(sense.active_power)
        currSolar = int(sense.active_solar_power)
        #print(self.lastCall, self.updateInterval, time())
        if (time() > self.lastCall + self.updateInterval):
            difference = currSolar - currPower
            logging.info("Available Solar: %s, ActivePower: %sW, ActiveSolar: %sW", difference, currPower, currSolar)
            self.lastCall = time()
            if (self.charging and difference > 0):
                logging.info("charging")
            elif (difference > (self.chargeW + (self.chargeW * 0.10))):
                self.startCharging()
            else:
                self.startDischarging()
                
    def startCharging(self):
        logging.info("start charging")
        self.charging = True
        self.setLED(ledPinCharge)
        #enable pins for relay
        
    def startDischarging(self):
        logging.info("start discharging")
        self.charging = False
        self.setLED(ledPinDischarge)
        #enable pins for relay
    
    def setLED(self, ledPin):
        GPIO.output(ledPinDischarge, GPIO.LOW)
        GPIO.output(ledPinCharge, GPIO.LOW)
        GPIO.output(ledPin, GPIO.HIGH)

sC = senseController()
try:
    while True:
        logging.info("begin update_realtime")
        sense.update_realtime(sC.webSocketCallback)
        logging.warning("update_realtime failed, end loop")
except:
    logging.exception('')
finally:
    logging.info("end SenseController")
    GPIO.cleanup()

