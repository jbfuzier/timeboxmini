import timebox
import paho.mqtt.client as mqtt
import config
import time
import base64
import StringIO
import json
import ast
import datetime
import sys
import traceback
import os
import logging
import logging.config


logging_conf = { 
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': { 
        'standard': { 
            'format': '%(asctime)-15s - %(process)d [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': { 
        'default': { 
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'debug.log',
            'maxBytes': 10*1024*1024,
            'backupCount': 5,
        },
    },
    'loggers': {
        '': { 
            # 'handlers': ['default', 'file', 'mail'],
            'handlers': ['default', 'file'],
            'level': 'DEBUG',
            'propagate': True
        },
    } 
}

logging.config.dictConfig(logging_conf)


client = mqtt.Client()
t = timebox.TimeBox()

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logging.warning("Connected with result code "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(config.mqtt_topic+"/in")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8', errors='replace')
    logging.debug(msg.topic+" "+payload)
    payload_response = {'time': str(datetime.datetime.now())}
    try:
        payload = ast.literal_eval(payload) # Safe to unserialize untrusted data with this
        if 'id' in payload:
            payload_response['id'] = payload['id']
        if not 'action' in payload:
            raise Exception("Mandatory field 'action' is missing")
        action = payload['action']
        if action=="show_clock":
            color = None
            if 'color' in payload:
                color = payload['color']
            t.show_clock(color)
        elif action=='show_static_image' or action=='show_animated_image':
            if 'path' in payload:
                path = os.path.normpath(payload['path'])
                if not path.split(".")[-1].lower() in ['png', 'bmp', 'gif']:
                    # TODO : check is this is robust enough security wise to avoid
                    # arbitrary file information leakage
                    raise Exception("Unsupported file extension")
                if not os.path.exists(path):
                    raise Exception("path %s does not exists"%path)
                if action=='show_static_image':
                    t.show_static_image(path) # Seems scary for security
                else:
                    t.show_animated_image(path)
            elif 'data' in payload:
                #Base64 encoded git or png data
                data = base64.b64decode(payload['data'])
                data = StringIO.StringIO(data)
                if action=='show_static_image':
                    t.show_static_image(data)
                else:
                    t.show_animated_image(data)
        elif action=='show_text':
            text = []
            for txt, color in payload['text']:
                text.append((txt, color))
            if 'speed' in payload:
                t.show_text(text, font=config.font, speed=payload['speed'])
            else:
                t.show_text(text, font=config.font)
        elif action=='ack' or action=='exception':
            return
        else:
            raise Exception("Unknwon action")
        payload_response['action'] = 'ack'
        client.publish(config.mqtt_topic+"/out", payload=json.dumps(payload_response))
    except Exception as e:
        # type, value, traceback = sys.exc_info()
        msg = "Got exception : %s : %s"%(e, traceback.format_exc())
        logging.error(msg)
        payload_response['action'] = 'exception'
        payload_response['msg'] = msg
        client.publish(config.mqtt_topic+"/out", payload=json.dumps(payload_response), qos=0, retain=False)


client.on_connect = on_connect
client.on_message = on_message
client.will_set(config.mqtt_topic+"/out", payload=json.dumps({'action': 'daemon_died'}), qos=0, retain=False)

client.connect(config.mqtt_server[0], config.mqtt_server[1], 60)

if __name__ == '__main__':
    for i in range(10):
        try:
            t.connect()
        except Exception as e:
            logging.error("Got exception while attempting to connect to timebox : %s"%e)
            time.sleep(10)
            continue
        break
    t.set_time()
    client.loop_forever()