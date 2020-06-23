#Script to drive transilluminator
#Called every minute from the crontab
#Irradiates with blue light of varying intensity, before
#switching to green to generate fluorescence and taking
#a photo
#Donora 27/02/2020

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
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import glob

pixels = neopixel.NeoPixel(board.D18, 96)

current_milli_time = lambda: int(round(time.time() * 1000))
Atemp = np.empty((0,2)) # set upper limit of number of entries - this is more efficient than addenda
Ahum = np.empty((0,2))  # ditto
startmilli = current_milli_time()

#Set up pins for fan control
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)

#SET VARIABLES HERE
###################
g = 30 # Update gif every x minutes (APPROX) (Takes up to a few mins)
maxgifimages = 10 # definitely less than 100 to avoid slowdown
###################
#COLOURS
###################
blue = (0,0,255)
green = (0,255,0)
###################

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


#####################
#Flags
dicts = {
'RunProtocol' : 0,
'EndProtocol' : 0,
'LockParameters' : 0,
'BlueTime' : 0.0,
'GreenTime' : 0.0,
'Duration' : 0,
'SetTemp' : 0.0,
'TimeStart' : 'null',
'DateStart' : 'null',
'CronCount' : 0,
'Counter' : 0}
#Duration is in days; set to 0 for no set ending
#Green time in seconds
#Blue time in minutes

#internal flag to avoid writing the config file with null values
allowconfigwrite = 0

#####################

#read from config file
def readfromconfig():
    global dicts
    global allowconfigwrite
    try:
        with open('config.txt', 'r') as config:
            for line in config:
                if len(line) > 3:
                    (key, val) = line.split(',')
                    dicts[key] = val
            print("read from config (first try)")
        allowconfigwrite = 1
    except:
        try:
            print("failed first read; trying again")
            time.sleep(1)
            with open('config.txt', 'r') as config:
                for line in config:
                    if len(line) > 3:
                        (key, val) = line.split(',')
                        dicts[key] = val
                print("read from config (second try)")
            allowconfigwrite = 1
        except:
            allowconfigwrite = 0
            print("failed on second try as well")

#Write to config file
def writetoconfig():
    global dicts
    global allowconfigwrite
    if allowconfigwrite == 1:
        try:
            with open('config.txt', 'w') as config:
                for key, val in dicts.items():
                    config.write(str(key) + "," + str(val) + "\n")
                print("wrote to config")
        except:
            print(" config file opening failed (writetoconfig)")

def fanon():
    GPIO.output(23, GPIO.HIGH)

def fanoff():
    GPIO.output(23, GPIO.LOW)

def gentime():
    now = datetime.now() #Get the date+time right now
    global date
    date = now.strftime("%Y/%m/%d") #The function for writing the date and time
    global timenow
    timenow = now.strftime("%H:%M:%S") #for file output

def gentimepic():
    now = datetime.now() #Get the date+time right now
    global datepic
    datepic = now.strftime("%Y%m%d") #The function for writing the date and time
    global timenowpic
    timenowpic = now.strftime("%H%M%S") #for file output

def gettemphum():
    ht = Adafruit_DHT.read_retry(11,4)
    global temp
    temp = ht[1]
    global hum
    hum = ht[0]

###############################################################
### Illumination in horizontal stripes of varying intensity ###
def stripeillum():
    print('setting blue...')

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

def gifupdate():
    os.system('sudo rm gifstills/*')
    print('Making GIF...')
    mo=1+math.floor(len(glob.glob("stills/*.jpg"))/maxgifimages)
    for it, file in enumerate([os.path.basename(x) for x in glob.glob("stills/*.jpg")]):
        if it%mo == 0:
            os.system('sudo cp stills/%s gifstills/%s' % (file, file))
    os.system('sudo convert -delay 40 -loop 0 gifstills/* static/timelapse.gif')


#open camera elsewhere
res = (820, 616) #native resolution /4 (true res 3280x2464)
camera = PiCamera(resolution=res, framerate=2)
def takeimage(tgreen):
    print('trying to start camera...')
    # CAMERA SETUP
    ###################
    #res = (1280, 720) #720p
#    camera.close()
    # Set ISO to the desired value
    camera.iso = 100
    # Wait for the automatic gain control to settle
    time.sleep(1)
    # Now fix the values
    camera.shutter_speed = 500000
    camera.exposure_mode = 'off'
    #set_analog_gain(camera,1)
    #set_digital_gain(camera,1)
    #camera.analog_gain = (camera,1)
    #camera.digital_gain = (camera,1)
    camera.awb_mode = 'off'
    camera.awb_gains = (1,1)
    print('Camera Started')


    pixels.fill(green)
    pixels.show()
    time.sleep(tgreen)
    #get time now
    gentimepic()
    #TAKE IMAGE
    camera.iso = 800
    #log file:
    print("Iteration " + str(dicts['Counter']) + ", ISO 800")
    #take image
    print('Taking picture...')
    camera.capture('stills/Snap'+datepic+timenowpic+'.jpg')
    print('Picture taken')
    camera.close()
    print('Camera Closed')
    os.system('sudo cp stills/Snap%s%s.jpg static/Latest.jpg' % (datepic,timenowpic))

def writetolog(mins, temp, hum):
    with open('thlog.txt', 'a+') as log:
        log.write(str(mins) + ',' + str(temp) + ',' + str(hum) + '\n')

def plotgraph():
    global Atemp
    global Ahum
    Atemp = np.empty((0,2))
    Ahum = np.empty((0,2))
    with open('thlog.txt', 'r') as log:
        for line in log:
            if len(line) > 3:
                (mins,tem,hu) = line.strip('\n').split(',')
                mins = float(mins)
                tem = float(tem)
                hu = float(hu)
                Atemp = np.vstack((Atemp, [mins, tem]))
                Ahum = np.vstack((Ahum, [mins, hu]))
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(Atemp[:,0], Atemp[:,1], label = 'Temperature')
    ax1.plot(Ahum[:,0], Ahum[:,1], label = 'Humidity')
    plt.legend(loc='upper left')
    plt.xlabel('Minutes')
    plt.ylabel('Celsius / % Humidity')
    plt.savefig('static/plotTempHum.png')
    plt.close()


#######################
#BEGIN SCRIPT#
#######################


#Read config file
if os.path.exists("config.txt"):
    try:
        with open('config.txt', 'r') as config:
            for line in config:
                if len(line) > 3:
                    (key, val) = line.strip("\n").split(',')
                    dicts[key] = val
#            print("read config for initial setup")
            allowconfigwrite=1
    except:
        allowconfigwrite = 0
#        print("initial config file opening failed")

if int(dicts['CronCount']) == 0:
    open('thlog.txt', 'w+').close()
    open('output.txt', 'w+').close()

#Regardless:
##CRONTAB UPDATE
dicts['CronCount'] = int(dicts['CronCount']) +1

#if protocol is live
if int(dicts['RunProtocol']) == 1:
#    print('if protocol is live flag yes')
    gettemphum()
    if temp > float(dicts['SetTemp']):
        fanon()
    else:
        fanoff()

#if protocol is live and if enough minutes of blue light have run:
if int(dicts['RunProtocol']) == 1 and int(dicts['CronCount'])%int(float(dicts['BlueTime'])) == 0:
####################
#    print('if protocol is live and mins blue light flag yes')
    print('CronCout = ' + str(dicts['CronCount']))
    dicts['Counter'] = int(dicts['Counter'])+1
    print('counter increased')
    gentime()
    gettemphum()
    print('Time: ' + str(timenow))
    mins = int(dicts['CronCount'])
    takeimage(float(dicts['GreenTime']))
    stripeillum()
    writetolog(mins, temp, hum)
    plotgraph()
#    writetoconfig()

#if protocol is live and if enough minutes of have run:
if int(dicts['RunProtocol']) == 1 and int(dicts['CronCount'])%g == 0:
    gifupdate()

if int(dicts['EndProtocol']) == 1:
    gentimepic()
    #Move data to store
    #Save to github?
    dicts['EndProtocol'] = 0
    dicts['RunProtocol'] = 0
    dicts['LockParameters'] = 0
    dicts['CronCount'] = 0
    dicts['Counter'] = 0
#    save anything important from output.txt
#    open('output.txt', 'w').close()
    os.system('sudo mkdir backupstills%s%s' % (datepic, timenowpic))
    os.system('sudo mkdir backupfiles%s%s' % (datepic, timenowpic))
    os.system('sudo mv stills/* backupstills%s%s/' % (datepic, timenowpic))
    try:
        os.system('sudo mv static/timelapse.gif backupfiles%s%s/timelapse%s%s.gif' % (datepic, timenowpic, datepic, timenowpic))
    except:
        print('No timelapse gif to move')
    os.system('sudo cp thlog.txt backupfiles%s%s/thlog%s%s.txt' % (datepic, timenowpic, datepic, timenowpic))
    os.system('sudo cp output.txt backupfiles%s%s/output%s%s.txt' % (datepic, timenowpic, datepic, timenowpic))
#    writetoconfig()
    fanoff()
    pixels.fill((0,0,0))
    pixels.show()

writetoconfig()
#in case of error
camera.close()
print('Camera Closed (end)')
gentime()
print('End time: ' + str(timenow))
