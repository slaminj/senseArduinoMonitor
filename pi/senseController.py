from secrets import SENSE_PASS, SENSE_USER
from sense_energy  import Senseable
from time import time, gmtime, strftime
import logging
logging.basicConfig(filename='output.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s %(message)s')

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

    def webSocketCallback(self, error):
        print("heartbeat. error: ", error)
        if (error):
            sense.update_realtime(sC.webSocketCallback)
            #return
        currPower = int(sense.active_power)
        currSolar = int(sense.active_solar_power)
        print(self.lastCall, self.updateInterval, time())
        if (time() > self.lastCall + self.updateInterval):
            logging.info("ActivePower: %sW, ActiveSolar: %sW", currPower, currSolar)
            difference = currSolar - currPower
            self.lastCall = time()
            if (self.charging and difference > 0):
                logging.info("charging")
            elif (difference > (self.chargeW + (self.chargeW * 0.10))):
                self.startCharging()
            else:
                self.startDischarging();
                
    def startCharging(self):
        logging.info("start charging")
        #enable pins for relay
        
    def startDischarging(self):
        logging.info("start discharging")
        #enable pins for relay
            
        
sC = senseController()
sense.update_realtime(sC.webSocketCallback)
