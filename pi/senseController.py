from secrets import SENSE_PASS, SENSE_USER
from sense_energy  import Senseable

sense = Senseable()
sense.authenticate(SENSE_USER, SENSE_PASS)

class senseController:

    pastPower= 0
    pastSolar= 0

    def webSocketCallback(self):
        # sense.update_trend_data()
        currPower = int(sense.active_power)
        if currPower != self.pastPower:
            print ("Active:", currPower, "W")
            self.pastPower = currPower

        currSolar = int(sense.active_solar_power)
        if currSolar != self.pastSolar:
            print ("Active Solar:", currSolar, "W")
            self.pastSolar = currSolar
        # print ("Daily:", sense.daily_usage, "KWh")
        # print ("Daily Solar:", sense.daily_production, "KWh")
        # print ("Active Devices:",", ".join(sense.active_devices)) 
sC = senseController()
sense.update_realtime(sC.webSocketCallback)