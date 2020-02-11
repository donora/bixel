# Bixel

A script and hardware design for creating a low-cost plate reader using a raspberry pi and lego!

1. Equipment/Parts
2. Code

## Equipment

- Raspberry pi (zero, 3 or 4)
- raspicam
- DHT 11 sensor
- [Adafruit neopixel](https://www.adafruit.com/product/1487) 
- Optical filters
- Fan

Insert image
![Image detail to appear if image doesn't load](images/--imagename--.jpg)


## Code

To Run:

Install nginx
`sudo apt intall nginx`

Edit the default file to point to your bixel directory. If you are using a raspi as user pi then your directory will be `\home\pi\bixel`

`sudo nano \etc\nginx\sites-available\default`

type ctrl+w and enter root to find the line:
``


<html>
<head>
<title>Bixel output screen</title>
</head>
<body>
<center>
<h1>Bixel output screen</h1>
<h2>ISO 100: First and Latest Images</h2>
<a href="cam/First.jpg">
<img src="cam/First.jpg" alt="First_Image" height="308" width="410" ></a>
<a href="cam/Latest.jpg">
<img src="cam/Latest.jpg" alt="Latest_Image" height="308" width="410" ></a>

<h2>ISO 800: First and Latest Images</h2>
<a href="cam/FirstExp2.jpg">
<img src="cam/FirstExp2.jpg" alt="First_Image_Exp2" height="308" width="410" ></a>
<a href="cam/LatestExp2.jpg">
<img src="cam/LatestExp2.jpg" alt="Latest_Image_Exp2" height="308" width="410" ></a>

<h2>Temperature & Humidity Graph, Timeline GIF</h2>
<a href="cam/plotTempHum.png">
<img src="cam/plotTempHum.png" alt="TemperatureHumidity" height="308" width="410" ></a>

<a href="cam/timelapse.gif">
<img src="cam/timelapse.gif" alt="timelapse" height="308" width="410" ></a>
</center>
</body>
</html>
