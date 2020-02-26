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

runProtocol=1

current_milli_time = lambda: int(round(time.time() * 1000))
startmilli = current_milli_time()

def test():
    print("Test success")

def fanon():
    GPIO.output(23, GPIO.HIGH)
    global fanstatus
    fanstatus = 'On'

def fanoff():
    GPIO.output(23, GPIO.LOW)
    global fanstatus
    fanstatus = 'Off'

time.sleep(0.1)
def gentime():
    now = datetime.now() #Get the date+time right now
    # dd/mm/YY H:M:S  #The format for the date and time Date/month/Year Hour:Minute$
    global date
    date = now.strftime("%Y/%m/%d") #The function for writing the date and time
    global exact_time
    exact_time = now.strftime("%H:%M:%S") #for file output

def gettemphum():
    ht = Adafruit_DHT.read_retry(11,4)
    global temp
    temp = ht[1]
    global hum
    hum = ht[0]

@app.route("/")
def index():
    gettemphum()
    gentime()
    templateData = {
    'nothome' : 0,
    'title' : 'Temperature and Humidity',
    'temp' : temp,
    'fanstat' : fanstatus,
    'hum' : hum,
    'date' : date,
    'time' : exact_time
    }
    return render_template('index.html', **templateData)

@app.route("/test")
def dothis():
    gettemphum()
    gentime()
    templateData = {
    'nothome' : 0,
    'title' : 'Temperature and Humidity',
    'temp' : temp,
    'fanstat' : fanstatus,
    'hum' : hum,
    'date' : date,
    'time' : exact_time
    }
    return render_template('index.html', **templateData), test()

def fanprotocol(t,repeats,interval):
    for i in range(repeats):
        fanon()
        time.sleep(t)
        fanoff()
        time.sleep(interval)
    print("Fan protocol done")

@app.route("/<deviceName>/<action>", methods=['GET', 'POST'])
def action(deviceName, action):
    global t
    global interval
    global repeats
    t = float(request.form['runtime'])
    interval = int(request.form['interval'])
    repeats = int(request.form['repeats'])

#    if runProtocol == 1:
#        for i in range(repeats):
#            fanon()
#            time.sleep(t)
#            fanoff()
#            time.sleep(interval)

    gentime()
    gettemphum()
    templateData= {
        'fanstat' : fanstatus,
        'title' : 'Temperature & Humidity',
        'temp' : temp,
        'hum' : hum,
        'date' : date,
        'time' : exact_time
    }
    if runProtocol == 1:
        return render_template('index.html', **templateData), fanprotocol(t, interval, repeats)
    else:
        return render_template('index.html', **templateData)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
