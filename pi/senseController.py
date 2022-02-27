from secrets import SENSE_PASS, SENSE_USER
from sense_energy  import Senseable

sense = Senseable()
sense.authenticate(SENSE_USER, SENSE_PASS)
sense.update_realtime()
# sense.update_trend_data()
print ("Active:", sense.active_power, "W")
print ("Active Solar:", sense.active_solar_power, "W")
print ("Daily:", sense.daily_usage, "KWh")
print ("Daily Solar:", sense.daily_production, "KWh")
# print ("Active Devices:",", ".join(sense.active_devices)) 