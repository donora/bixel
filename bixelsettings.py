import os
import Adafruit_DHT
from flask import Flask, render_template, request
app = Flask(__name__)
import time
from datetime import datetime
import RPi.GPIO as GPIO

#Set up pin for fan control
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(23, GPIO.OUT)
fanstatus = 'Off'

#Flags
dicts = {
'RunProtocol' : 0,
'EndProtocol' : 0,
'LockParameters' : 0,
'BlueTime' : 0.0,
'GreenTime' : 0.0,
'Duration' : 0,
'SetTemp' : 0.0}
#Duration is in days; set to 0 for no set ending
#Green time in seconds
#Blue time in minutes

#Read or create config file
if os.path.exists("config.txt"):
    try:
        with open('config.txt', 'r') as config:
            for line in config:
                if len(line) > 0:
                    (key, val) = line.strip("\n").split(',')
                    dicts[key] = val
            print("read config for initial setup")
    except:
        print("initial config file opening failed")
else:
    with open('config.txt', 'w') as config:
        for key, val in dicts.items():
            config.write(str(key) + "," + str(val) + "\n")
        print("created config file")

#read from config file
def readfromconfig():
    global dicts
    try:
        with open('config.txt', 'r') as config:
            for line in config:
                if len(line) > 0:
                    (key, val) = line.split(',')
                    dicts[key] = val
            print("read from config (first try)")
    except:
        time.sleep(1)
        with open('config.txt', 'r') as config:
            for line in config:
                if len(line) > 0:
                    (key, val) = line.split(',')
                    dicts[key] = val
            print("read from config (second try)")


def writetoconfig():
    global dicts
    try:
        with open('config.txt', 'w') as config:
            for key, val in dicts.items():
                config.write(str(key) + "," + str(val) + "\n")
            print("wrote to config")
    except:
        print(" config file opening failed (writetoconfig)")

current_milli_time = lambda: int(round(time.time() * 1000))
startmilli = current_milli_time()

def gentime():
    now = datetime.now() #Get the date+time right now
    global date
    date = now.strftime("%Y/%m/%d") #The function for writing the date and time
    global timenow
    timenow = now.strftime("%H:%M:%S") #for file output

def gettemphum():
    ht = Adafruit_DHT.read_retry(11,4)
    global temp
    temp = ht[1]
    global hum
    hum = ht[0]

timestart = 'unset'
datestart = 'unset'

@app.route("/")
def index():
    global dicts
    global timestart
    global datestart
    gettemphum()
    gentime()
    readfromconfig()
    templateData = {
    'title' : 'Home',
    'RunProtocol' : int(dicts['RunProtocol']),
    'timestart' : timestart,
    'datestart' : datestart,
    'temp' : temp,
    'hum' : hum,
    'date' : date,
    'time' : timenow
    }
    return render_template('index.html', **templateData)

@app.route("/configure")
def configure():
    global dicts
    readfromconfig()
    gettemphum()
    gentime()
    templateData = {
    'title' : 'Configure Settings',
    'RunProtocol' : int(dicts['RunProtocol']),
    'BlueTime' : float(dicts['BlueTime']),
    'GreenTime' : float(dicts['GreenTime']),
    'Duration' : float(dicts['Duration']),
    'SetTemp' : float(dicts['SetTemp']),
    'temp' : temp,
    'hum' : hum,
    'date' : date,
    'time' : timenow
    }
    return render_template('configure.html', **templateData)


@app.route("/confirm", methods=['GET', 'POST'])
def confirm():
    global dicts
    readfromconfig()
    dicts['RunProtocol'] = 1
    dicts['EndProtocol'] = 0
    dicts['LockParameters'] = 1
    dicts['BlueTime'] = float(request.form['BlueTime']) #minutes
    dicts['GreenTime'] = float(request.form['GreenTime']) #seconds
    dicts['Duration'] = float(request.form['Duration']) #days
    dicts['SetTemp'] = float(request.form['SetTemp'])
    try:
        writetoconfig()
    except:
        dicts['RunProtocol'] = 0
    gentime()
    global timestart
    global datestart
    timestart = timenow
    datestart = date
    gettemphum()
    templateData= {
        'title' : 'Confirm Protocol',
        'RunProtocol' : int(dicts['RunProtocol']),
        'temp' : temp,
        'hum' : hum,
        'date' : date,
        'time' : timenow,
        'BlueTime' : float(dicts['BlueTime']),
        'GreenTime' : float(dicts['GreenTime']),
        'Duration' : float(dicts['Duration']),
        'SetTemp' : float(dicts['SetTemp']),
    }

    return render_template('confirm.html', **templateData)

@app.route("/view")
def view():
    global dicts
    global timestart
    global datestart
    gentime()
    gettemphum()
    readfromconfig()
#FIND IMAGES for etc
    templateData= {
        'title' : 'Data View',
        'temp' : temp,
        'timestart' : timestart,
        'datestart' : datestart,
        'hum' : hum,
        'date' : date,
        'time' : timenow,
        'RunProtocol' : int(dicts['RunProtocol']),
        'BlueTime' : float(dicts['BlueTime']),
        'GreenTime' : float(dicts['GreenTime']),
        'Duration' : float(dicts['Duration']),
        'SetTemp' : float(dicts['SetTemp']),
    }
    return render_template('view.html', **templateData)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
