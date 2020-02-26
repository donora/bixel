import os
import Adafruit_DHT
from flask import Flask, render_template, request
app = Flask(__name__)
import time
from datetime import datetime

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
'DateStart' : 'null'}
#Duration is in days; set to 0 for no set ending
#Green time in seconds
#Blue time in minutes

#internal flag to avoid end of experiment by manual
#navigation to /end page
endroute = 0

#internal flag to notify user that protocol was not successfully
#written to config file (and therefore did not start)
startfailflag = 0

#####################

#Read or create config file
if os.path.exists("config.txt"):
    try:
        with open('config.txt', 'r') as config:
            for line in config:
                if len(line) > 3:
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
                if len(line) > 3:
                    (key, val) = line.split(',')
                    dicts[key] = val
            print("read from config (first try)")
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
        except:
            print("failed on second try as well")

#Write to config file
def writetoconfig():
    global dicts
    try:
        with open('config.txt', 'w') as config:
            for key, val in dicts.items():
                config.write(str(key) + "," + str(val) + "\n")
            print("wrote to config")
    except:
        print(" config file opening failed (writetoconfig)")

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

@app.route("/")
def index():
 #internal flags
    global endroute
    endroute = 0
#
    global dicts
    gettemphum()
    gentime()
    readfromconfig()
    templateData = {
    'title' : 'Home',
    'RunProtocol' : int(dicts['RunProtocol']),
    'LockParameters' : int(dicts['LockParameters']),
    'timestart' : dicts['TimeStart'],
    'datestart' : dicts['DateStart'],
    'temp' : temp,
    'hum' : hum,
    'date' : date,
    'time' : timenow
    }
    return render_template('index.html', **templateData)

@app.route("/configure")
def configure():
#internal flags
    global endroute
    endroute = 0
#
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
#internal flags
    global endroute
    global startfailflag
    startfailflag = 0
    endroute = 0
#
    global dicts
    readfromconfig()
    dicts['RunProtocol'] = 1
    dicts['EndProtocol'] = 0
    dicts['LockParameters'] = 1
    dicts['BlueTime'] = float(request.form['BlueTime']) #minutes
    dicts['GreenTime'] = float(request.form['GreenTime']) #seconds
    dicts['Duration'] = float(request.form['Duration']) #days
    dicts['SetTemp'] = float(request.form['SetTemp'])
    dicts['TimeStart'] = timenow
    dicts['DateStart'] = date
    try:
        writetoconfig()
    except:
        dicts['RunProtocol'] = 0
        dicts['LockParameters'] = 0
        print("failed to write to config during parameter dump.")
        startfailflag = 1
    gentime()
    gettemphum()
    templateData= {
        'title' : 'Confirm Protocol',
        'RunProtocol' : int(dicts['RunProtocol']),
        'temp' : temp,
        'startfailflag' : startfailflag,
        'hum' : hum,
        'date' : date,
        'time' : timenow,
        'timestart' : dicts['TimeStart'],
        'datestart' : dicts['DateStart'],
        'BlueTime' : float(dicts['BlueTime']),
        'GreenTime' : float(dicts['GreenTime']),
        'Duration' : float(dicts['Duration']),
        'SetTemp' : float(dicts['SetTemp'])
    }

    return render_template('confirm.html', **templateData)

@app.route("/view")
def view():
    global endroute
    endroute = 0
    global dicts
    gentime()
    gettemphum()
    readfromconfig()
#FIND IMAGES for etc
    templateData= {
        'title' : 'Data View',
        'temp' : temp,
        'timestart' : dicts['TimeStart'],
        'datestart' : dicts['DateStart'],
        'hum' : hum,
        'date' : date,
        'time' : timenow,
        'RunProtocol' : int(dicts['RunProtocol']),
        'LockParameters' : int(dicts['LockParameters']),
        'BlueTime' : float(dicts['BlueTime']),
        'GreenTime' : float(dicts['GreenTime']),
        'Duration' : float(dicts['Duration']),
        'SetTemp' : float(dicts['SetTemp'])
    }
    return render_template('view.html', **templateData)

@app.route("/endconfirm")
def endconfirm():
    global endroute
    endroute = 1
    templateData= {
        'title' : 'Confirm End Protocol',
    }
    return render_template('endconfirm.html', **templateData)

@app.route("/end")
def end():
    global endroute
    global dicts
    gentime()
    gettemphum()
    readfromconfig()
#FIND IMAGES for etc
    if endroute == 1:
        dicts['EndProtocol'] = 1
        dicts['StartProtocol'] = 0
        dicts['LockParameters'] = 0
        writetoconfig()
    templateData= {
        'endroute' : endroute,
        'title' : 'End Protocol',
        'temp' : temp,
        'timestart' : dicts['TimeStart'],
        'datestart' : dicts['DateStart'],
        'hum' : hum,
        'date' : date,
        'time' : timenow,
        'RunProtocol' : int(dicts['RunProtocol']),
        'RunProtocol' : int(dicts['RunProtocol']),
        'LockParameters' : int(dicts['LockParameters']),
        'BlueTime' : float(dicts['BlueTime']),
        'GreenTime' : float(dicts['GreenTime']),
        'Duration' : float(dicts['Duration']),
        'SetTemp' : float(dicts['SetTemp']),
    }
    endroute = 0
    return render_template('end.html', **templateData)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
