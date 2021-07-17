#!/usr/bin/env python3.6
"""

A small Test application to show how to use Flask-MQTT.

"""

import eventlet
import json
from flask import Flask, render_template
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_bootstrap import Bootstrap
import web_ui.base64_server as base64_server
from flask import Flask, request, send_from_directory
eventlet.monkey_patch()

app = Flask(__name__, static_url_path='/scripts')
app.config['SECRET'] = 'my secret key'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = 'ws.blackmirror.app'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False


# Parameters for SSL enabled
# app.config['MQTT_BROKER_PORT'] = 8883
# app.config['MQTT_TLS_ENABLED'] = True
# app.config['MQTT_TLS_INSECURE'] = True
# app.config['MQTT_TLS_CA_CERTS'] = 'ca.crt'

mqtt = Mqtt(app)
socketio = SocketIO(app)
bootstrap = Bootstrap(app)



@app.route('/')
def index():
    return render_template('example.html')

@app.route('/')
def static_file(path):
    return app.send_static_file(path)


@app.route('/favicon.ico')
def fav():
    return(base64_server.favicon)

@socketio.on('publish')
def handle_publish(json_str):
    print(f'Publishing {json_str}')
    data = json.loads(json_str)
    mqtt.publish(data['topic'], data['message'])


#app = Flask(__name__, static_url_path='')

@socketio.on('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    mqtt.subscribe(data['topic'])


@socketio.on('unsubscribe_all')
def handle_unsubscribe_all():
    mqtt.unsubscribe_all()


@mqtt.on_message() # TODO: All you have to do is fix this!
def handle_mqtt_message(client, userdata,message):
    print('received message: ' + message)
    #msg = json.loads(f"{{'data': f'{message.payload}'}}")
    ##topic = json.loads(f"{{'topic':' {message.topic}'}}")
    #topic = message.topic.encode()
    data = dict(
        topic=message.topic,
        payload=message.payload.decode(),
        qos=message.qos,
    )
    socketio.emit('mqtt_message', data=data)


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)


def main():

    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)

if __name__ == '__main__':
    main()