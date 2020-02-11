#Script to drive transilluminator
#Irradiates with blue light of varying intensity, before
#switching to green to generate fluorescence and taking
#a photo
#V6 - LED Driving and Full Camera Params
#     Dynamic Range Investigation
#     Sending images to webpage
#     Write to csv file
#     Turn fan on/off to reg temperature
#     Produce graph of temperature and humidity
#M Donora 06/12/2019

import math
import time
from datetime import datetime
import os
import numpy as np
import board
import neopixel
from picamera import PiCamera
import Adafruit_DHT
import RPi.GPIO as GPIO
from matplotlib import pyplot as plt
import glob
#import subprocess
pixels = neopixel.NeoPixel(board.D18, 96)

current_milli_time = lambda: int(round(time.time() * 1000))
Atemp = np.empty((5000,2)) # set upper limit of number of entries - this is more efficient than addenda
Ahum = np.empty((5000,2))  # ditto
startmilli = current_milli_time()

#Set up pin for fan control
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)

#MOVE IMAGES FROM STILLS FOLDER TO BACKUP FOLDER
os.system('sudo mv stills/* backupstills/')
#NOTE: THIS FOLDER WILL NEED TO BE CLEARED EVERY SO OFTEN;
#DO NOT RELY ON IT LONG TERM

#SET VARIABLES HERE
###################
tblue = 300 # Length of time in blue phase (seconds)
tgreen = 1 # Length of time in green phase (seconds)
            # NB: switching takes approx 0.5s and must be completed
            # before taking an image
cycles = 0 # For continuous loop set to 0
maxtemp = 28.4 # Set desired temperature in Celsius  (temp not guaranteed!)
g = 20 # Update gif every x minutes (APPROX) (Takes up to a few mins)
gifIter = int((g*60)/(tblue+20)) # i.e. update gif every gifIter iterations (APPROX)
maxgifimages = 40 # definitely less than 100 to avoid slowdown
###################
print('Blue Illumination: '+str(tblue)+' s\nTarget Temperature: '+str(maxtemp)+' C\nTarget GIF Remake Time: '+str(g)+' mins')
print('GIF Remake Iterations = '+str(gifIter)+'\n')
#COLOURS
###################
blue = (0,0,255)
green = (0,255,0)
###################

# CAMERA SETUP
###################
res = (820, 616) #native resolution /4 (true res 3280x2464)
#res = (1280, 720) #720p
camera = PiCamera(resolution=res, framerate=2)
# Set ISO to the desired value
camera.iso = 100
# Wait for the automatic gain control to settle
time.sleep(2)
# Now fix the values
camera.shutter_speed = 500000
camera.exposure_mode = 'off'

#set_analog_gain(camera,1)
#set_digital_gain(camera,1)
#camera.analog_gain = (camera,1)
#camera.digital_gain = (camera,1)
camera.awb_mode = 'off'
camera.awb_gains = (1,1)


#DEFINE CELL INTENSITIES
###################
# Generate levels of blue as follows,
# where i/x sets the ratio - i.e. x=2 is half intensity blue
# set more by copy/pasting this formula with more blues i.e. blue4, blue5
blue2 = tuple(int(i/2) for i in blue)
blue3 = tuple(int(i/4) for i in blue)
blue4 = tuple(int(i/8) for i in blue)
blue5 = tuple(int(i/16) for i in blue)
blue6 = tuple(int(i/24) for i in blue)
blue7 = tuple(int(i/48) for i in blue)
blue8 = tuple(int(i/96) for i in blue)


######################################
### CHANGE ROW VALUES AS NECESSARY ###
def StripeIllum(k):
    #ROWS:
    for i in range(96):
        #Row A
        if i%8 == 7:
            #CHANGE AS NECESSARY
            pixels[i] = blue
        #Row B
        if i%8 == 6:
            pixels[i] = blue2
        #Row C
        if i%8 == 5:
            pixels[i] = blue3
        #Row D
        if i%8 == 4:
            pixels[i] = blue4
        #Row E
        if i%8 == 3:
            pixels[i] = blue5
        #Row F
        if i%8 == 2:
            pixels[i] = blue6
        #Row G
        if i%8 == 1:
            pixels[i] = blue7
        #Row H
        if i%8 == 0:
            pixels[i] = blue8

    pixels.show()
    time.sleep(tblue)

    ##UPDATE GIF EVERY SO OFTEN
    if k%gifIter == 0: #SET TO 0 TO ENABLE, -1 TO DISABLE
        os.system('sudo rm gifstills/*')
        print('Making GIF...')
        mo=1+math.floor(len(glob.glob("stills/Exp2*.jpg"))/maxgifimages)
        for it, file in enumerate([os.path.basename(x) for x in glob.glob("stills/Exp2*.jpg")]):
            if it%mo == 0:
                os.system('sudo cp stills/%s gifstills/%s' % (file, file))
        os.system('sudo convert -delay 20 -loop 0 gifstills/* cam/timelapse.gif')

    pixels.fill(green)
    pixels.show()
    time.sleep(tgreen)
    #get time now
    gentime()
    #TAKE IMAGE
    camera.iso = 100
    #log file:
    write2log()
    print("Iteration " + str(k) + ", ISO 100")
    #take image
    camera.capture('stills/Snap'+date+exact_time+'.jpg')

    #TAKE IMAGE AT LONGER EXPOSURE
    camera.iso = 800
    #log file:
    write2log()
    print("ISO 800\n\n")
    #take image
    camera.capture('stills/Exp2_'+date+exact_time+'.jpg')

    #OUTPUT TO WEB - INITIAL AND CURRENT IMAGES
    if k == 1:
        os.system('sudo cp stills/Snap%s%s.jpg cam/First.jpg' % (date,exact_time))
        os.system('sudo cp stills/Exp2_%s%s.jpg cam/FirstExp2.jpg' % (date,exact_time))
    else:
        os.system('sudo cp stills/Snap%s%s.jpg cam/Latest.jpg' % (date,exact_time))
        os.system('sudo cp stills/Exp2_%s%s.jpg cam/LatestExp2.jpg' % (date,exact_time))

    time.sleep(0.1)
######################################
def fanon():
    GPIO.output(23, GPIO.HIGH)

def fanoff():
    GPIO.output(23, GPIO.LOW)

def gentime():
    now = datetime.now() #Get the date+time right now
    # dd/mm/YY H:M:S  #The format for the date and time Date/month/Year Hour:Minute$
    global date
    date = now.strftime("%Y_%m_%d") #The function for writing the date and time
    global exact_time
    exact_time = now.strftime("%H_%M_%S") #for file output
    global exact_t_excel
    exact_t_excel= now.strftime("%H:%M:%S") #for excel
    #return(date, exact_time, exact_t_excel)
######################################
######### WRITE TO LOG FILE ##########
def write2log():
    #OUTPUT LOG DATA
    #Get temp/humidity data
    #Also turns fan on/off for temp control
    ht = Adafruit_DHT.read_retry(11,4)
    #gentime()
    temp = ht[1]
    hum = ht[0]
    print('Time: '+str(round(((current_milli_time()-startmilli)/60000), 2))+' minutes')
    if temp > maxtemp:
        fanon()
        print('fan on, t='+str(temp)+'C, humidity='+str(hum)+'%')
    elif temp < maxtemp:
        fanoff()
        print('fan off, t='+str(temp)+'C, humidity='+str(hum)+'%')
    logfile = open('log.txt', 'a')
    logfile.write(str(k)+'\t'+date+'\t'+exact_t_excel+'\t'+str(temp)+'\t'+str(hum)+'\t'+str(camera.iso)+'\t'+str(camera.analog_gain)+'\t'+str(camera.digital_gain)+'\n')
    logfile.close()
    #update data
    Atemp[k-1] = [(current_milli_time()-startmilli)/60000,temp]
    Ahum[k-1] = [(current_milli_time()-startmilli)/60000, hum]
    #plot
    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    ax1.plot(Atemp[:k-1,0], Atemp[:k-1,1], label = 'Temperature')
    ax1.plot(Ahum[:k-1,0], Ahum[:k-1,1], label = 'Humidity')
    plt.legend(loc='upper left')
    plt.xlabel('Minutes')
    plt.ylabel('Celsius / % Humidity')
    plt.savefig('plotTempHum.png')
    plt.close()
    #send to html page
    os.system('sudo cp plotTempHum.png cam/plotTempHum.png')
######################################

######################################
####### FULL BLUE ILLUMINATION #######
def BlockIllum(k):
    pixels.fill(blue)
    pixels.show()
    time.sleep(tblue)

    pixels.fill(green)
    pixels.show()
    time.sleep(tgreen)
    camera.capture('stills/Snap' + str(k) + '.jpg')
    time.sleep(1)
######################################
######################################

######################################
############ PROGRAM BEGIN ###########
######################################

#Fan On
fanon()

# Get current date
gentime()

#INITIALISE FILE
###################
logfile = open('log.txt', 'w+')
logfile.write('--TAB SEPARATED DATA FILE--\nCAMERA SETTINGS:\nResolution = '+str(res)+'\nShutter speed = '+str(camera.shutter_speed)+' microseconds\n')
logfile.write('LED CYCLE:\nBlue Illumination: '+str(tblue)+'s\nGreen Illumination: '+str(tgreen)+'s\nNumber of Cycles: '+str(cycles)+' <-- (0 is continuous loop)\n\n')
logfile.write('ITERATION\tDATE\tTIME\tTEMPERATURE\tHUMIDITY\tISO\tANALOG GAIN\tDIGITAL GAIN\t\n')
logfile.close()
###################


camera.start_preview()
# Camera warm-up time
time.sleep(2)

k=1
if cycles > 0:
    for c in range(cycles):

        #FOR ALL ROWS FULL BLUE, UNCOMMENT THIS:
        #BlockIllum()
        #AND COMMENT THIS:
        StripeIllum(k)
        k=k+1

elif cycles == 0:
    while cycles < 1:

        #FOR ALL ROWS FULL BLUE, UNCOMMENT THIS:
        #BlockIllum()
        #AND COMMENT THIS:
        StripeIllum(k)
        k=k+1

##Turn Off##
pixels.fill((0,0,0))
pixels.show()
