import sys
sys.path.append('./sense_energy')
from secrets import SENSE_PASS, SENSE_USER
from sense_energy  import Senseable
from time import time, gmtime, strftime
import logging
logging.basicConfig(filename='output.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')

import RPi.GPIO as GPIO
import board
import digitalio
import adafruit_character_lcd.character_lcd as characterlcd
lcd_rs = digitalio.DigitalInOut(board.D26)
lcd_en = digitalio.DigitalInOut(board.D19)
lcd_d4 = digitalio.DigitalInOut(board.D25)
lcd_d5 = digitalio.DigitalInOut(board.D24)
lcd_d6 = digitalio.DigitalInOut(board.D22)
lcd_d7 = digitalio.DigitalInOut(board.D27)

lcd_columns = 16
lcd_rows = 2
lcd = characterlcd.Character_LCD_Mono(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows)
lcd.message = "startup.."

# GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
ledPinCharge = 6
ledPinDischarge = 5
GPIO.setup(ledPinCharge, GPIO.OUT)
GPIO.setup(ledPinDischarge, GPIO.OUT)
GPIO.output(ledPinDischarge, GPIO.LOW)
GPIO.output(ledPinCharge, GPIO.LOW)

sense = Senseable()
sense.authenticate(SENSE_USER, SENSE_PASS)
lcd.message = "authenticate.."

class senseController:

    pastPower= 0
    pastSolar= 0
    updateInterval = 3
    lastCall = 0
    
    chargeW = 100
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
            lcd.clear()
            lcd.message= "*:"+str(difference)+"W extra"
            if (self.charging and difference > 0):
                logging.info("charging")
                lcd.cursor_position(0,1)
                lcd.message= "charging"
            elif (difference > (self.chargeW + (self.chargeW * 0.10))):
                self.startCharging()
            else:
                self.startDischarging()
                
    def startCharging(self):
        logging.info("start charging")
        self.charging = True
        self.setLED(ledPinCharge)
        lcd.cursor_position(0,1)
        lcd.message= "start charging"
        #enable pins for relay
        
    def startDischarging(self):
        logging.info("start discharging")
        self.charging = False
        self.setLED(ledPinDischarge)
        lcd.cursor_position(0,1)
        lcd.message= "discharging"
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
    lcd.clear()
    lcd.message = "ERROR"
    GPIO.cleanup()

