import ADS1x15
import time
# initialize ADS1115 on I2C bus 1 with default address 0x48
ADS = ADS1x15.ADS1115(1)
# configuration things here
ADS.setMode(ADS.MODE_CONTINUOUS)
ADS.requestADC(0)               # request on pin 0
ADS.setGain(0)
ADS.setDataRate(7)



if ADS.isReady() :
    value = ADS.getValue()
    ADS.requestADC(0)           # request new conversion
# do other things here


while True :
    ADS.requestADC(0)
    value = ADS.getValue()
    print("Channel 0 Voltage:" + str(value))



    ADS.requestADC(1)
    value = ADS.getValue()
    print("Channel 1 Voltage:" + str(value))
   


    
   
    f= ADS.getMaxVoltage()
    ADS.requestADC(2)
    print("Channel 2 Voltage:" + str(ADS.toVoltage(f)))


    ADS.requestADC(3)
    print("Channel 3 Voltage:" + str(value))
    
   
    print("______________________")
    #time.sleep(1)