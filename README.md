# timeboxmini
Python mqtt daemon to talk with timebox mini

Most of the code comes from the work of derHeinz/divoom-adapter, DaveDavenport/timebox, MarcG046/timebox.

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

You need the MQTT plugin configured and enabled. And config.py configured with the IP of the jeedom.


Launch timebox_mqtt_daemon.py


Run timebox_mqtt_client.py, it will send some command to the daemon through the mqtt server. The timebox should react.


Go in the Mqtt config on jeedom, you should get a new device :


![image](https://user-images.githubusercontent.com/4688432/34258838-1d09aa40-e660-11e7-8b8d-3b382865b5fd.png)

Enable it : 


![image](https://user-images.githubusercontent.com/4688432/34258843-2193f368-e660-11e7-9d0e-fb628b4ccb3d.png)


Go to commands : 


![image](https://user-images.githubusercontent.com/4688432/34258848-24092258-e660-11e7-8154-c77ae64fb849.png)


Then add some actions : 


![image](https://user-images.githubusercontent.com/4688432/34258852-271c7ae4-e660-11e7-9f38-51048f9f501c.png)
![image](https://user-images.githubusercontent.com/4688432/34258855-2999f472-e660-11e7-92fd-0e0033f09da8.png)


Here are some examples of actions : 


Name|Subtype|topic|Payload
---|---|---|----
show_clock|default|timebox/in|{'action': 'show_clock'}|
show_clock_color|color|timebox/in|{'action': 'show_clock', 'color': '#color#'}|
show_text|Message|timebox/in|{'action': 'show_text', 'speed': 20, 'text': [('#message#', '#title#')]}|This trick allows to use the title field to set the text color



Example of show_text on the widget : 


![image](https://user-images.githubusercontent.com/4688432/34258857-2d1dab16-e660-11e7-9ad5-c3ef29cc9ec7.png)


Those actions can then be used on scenarios ex : 


![image](https://user-images.githubusercontent.com/4688432/34258861-2f9c2624-e660-11e7-96d2-e54d0431a0a6.png)


Commands accepted by the mqtt daemon : 
```	{'action': 'show_clock'}
	{'action': 'show_clock', 'color': 'red'}
	{'action': 'show_text', 'speed': 10, 'text': [('Hello', 'blue'),(' World','red')]}
	{'action': 'show_static_image', 'path': '../testdata/color.png'}
	{'action': 'show_animated_image', 'path': '../testdata/exp.gif'}
	{'action': 'show_static_image', 'data': 'iVBORw0KGgoAAAANSUhEUgAAAAsAAAALCAYAAACprHcmAAAACXBIWXMAAA4mAAAN/wHwU+XzAAAAXElEQVQYlc2PQQ6AQAgDB1/en48HdjVr9qA3IQRKS1IQNKiMVBpqYoz26MGHOAAqz3XtxQWYvabSRNVNaBCGZ+4yWTBOYgq1Md1jH1wPXjZkGRw2+n48+DZ+Ij4BeddPVF7LZ+sAAAAASUVORK5CYII='}
	{'action': 'show_animated_image', 'data': 'R0lGODlhCwALAKECAAAAAP8AAP///////yH/C05FVFNDQVBFMi4wAwEAAAAh/hFDcmVhdGVkIHdpdGggR0lNUAAh+QQBCgACACwAAAAACwALAAACCoSPqcvtGZ6c1BUAIfkEAQoAAwAsAAAAAAsACwAAAg+Ej6nLFv2ekoCiCJverAAAIfkEAQoAAwAsAAAAAAsACwAAAg+Ej6kaC22gY0lOJC2+XBUAIfkEAQoAAwAsAAAAAAsACwAAAg+Ejwmhm9yihE9aRU0++xYAIfkEAQoAAwAsAAAAAAsACwAAAg+EHXep2A9jZJDKi4FdbxcAIfkEAQoAAwAsAAAAAAsACwAAAgwMjmjJ7Q+jnJQuFwoAIfkEAQoAAwAsAAAAAAsACwAAAgqEj6nL7Q+jnKAAACH5BAEKAAMALAAAAAALAAsAAAIKhI+py+0Po5ygAAA7'}
```
	
	
```	
Color name : http://pillow.readthedocs.io/en/3.1.x/reference/ImageColor.html#module-PIL.ImageColor
Hexadecimal color specifiers, given as #rgb or #rrggbb. For example, #ff0000 specifies pure red.
Common HTML color names
4 LSB bits are dropped for each color channel 
```


### Cron
The following cron job, ensure that the daemon is running :

```
# Check is daemon is running, if not, run it
*/10 * * *  DIR="/root/timeboxmini/package/";PY="${DIR}/timebox_mqtt_daemon.py";APP="/usr/bin/python $PY";test -e "$PY"&&cd $DIR&&(pgrep -f "$APP">/dev/null||${APP}>/dev/null 2>&1)
```
