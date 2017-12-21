# timeboxmini
Python mqtt daemon to talk with timebox mini

Most of the code come from the work of derHeinz/divoom-adapter, DaveDavenport/timebox, MarcG046/timebox.

What works : 
* Display scrolling text
* Display static image (gif, bmp, png) by file path or from a b64 data blob
* Display animated image (gif) by file path or from a b64 data blob
* Display clock & change clock color


### 0. Requirements 
Bluetooth installed & configured with a bluetoth dongle.
On debian : `apt-get install bluetooth`

To check that the dongle is working properly : `blescan`

Python requirements (see requirements.txt) : `pip install -r requirements.txt`. A C compiler & bluetooth dev headers are required, on debian : `apt install libbluetooth-dev build-essential`


### 1. Quick start
Copy `config.py.sample` to `config.py` and edit it accordingly (put yours timebox mac address, `blescan` can help you getting it).

You can run timebox.py to test that communication with the timebox is working.

timebox_mqtt_daemon.py is a daemon that listens for command on a mqtt topic and send commands to the timebox mini accordingly.


### 2. Integration with jeedom
I use a daemon instead of a simple script, because when the script ends, connection to the timebox is closed and as a result the bluetooth icon on the timebox keeps blinking during several seconds...
