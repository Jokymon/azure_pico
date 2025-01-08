import az_client
import networking
import time
import ntptime
import machine
import json


# package installed through https://docs.micropython.org/en/latest/reference/packages.html
from umqtt.simple import MQTTClient
from machine import Pin

led = Pin("LED", Pin.OUT)
button = Pin(14, Pin.IN, Pin.PULL_DOWN)

topic_msg = b'{"buttonpressed":"1"}'
MQTT_PORT = 0

dm_request_sub = "$iothub/methods/POST/#"
twin_patch_sub = '$iothub/twin/PATCH/properties/reported/?$rid=%d'

dm_pub = '$iothub/methods/res/200/?$rid='


# Implementation based on https://learn.microsoft.com/en-us/azure/iot/iot-mqtt-connect-to-iot-hub#respond-to-a-direct-method
class DirectMethodHandler:
    def __init__(self):
        pass

    def dispatch(self, method_name, message):
        if hasattr(self, method_name):
            try:
                params = json.loads(message)
                res = getattr(self, method_name)(**params)
                return {"result": res}
            except Exception as e:
                return {"error": str(e)}
        else:
            return {"error": f"Method {method_name} unknown"}

    def hello(self, param1, param2):
        print(f"Called 'hello' with {param1} and {param2}")
        return "That is very good"


# All details of the MQTT protocol are from https://learn.microsoft.com/en-us/azure/iot/iot-mqtt-connect-to-iot-hub
class AzureClient:
    def __init__(self, dm_handler):
        self.dm = dm_handler
        self.client = None
        self.queue = []

    def process(self):
        self.client.check_msg()
        while len(self.queue) > 0:
            topic, message = self.queue.pop()
            self.client.publish(topic, message)

    def connect(self, config):
        self.config = config
        certificate_path = "baltimore.cer"
        print('Loading Blatimore Certificate')
        with open(certificate_path, 'r') as f:
            cert = f.read()
        sslparams = {'cert': cert}

        self.client = MQTTClient(client_id=config.deviceid,
                                 server=config.hostname,
                                 port=MQTT_PORT,
                                 user=config.username,
                                 password=config.password,
                                 keepalive=3600,
                                 ssl=True, ssl_params=sslparams)
        self.client.connect()
        print('Connected to IoT Hub MQTT Broker')

        self.client.set_callback(self.callback_handler)
        self.client.subscribe(topic="#")
        self.client.subscribe(topic=dm_request_sub)

    def reconnect(self):
        print('Failed to connect to the MQTT Broker. Reconnecting...')
        time.sleep(5)
        machine.reset()

    def callback_handler(self, topic, message_receive):
        # print(f"Received message on {topic}: {message_receive}")
        if b'devicebound' in topic:
            if message_receive.strip() == b'led_on':
                led.value(1)
            else:
                led.value(0)
        elif b'method' in topic:
            parts = topic.decode().split("/")
            method_name = parts[3]
            rid = parts[4]
            rid = rid.split("=")[1]

            res = self.dm.dispatch(method_name, message_receive)

            self.queue.append((dm_pub+rid, json.dumps(res)))

    def publish(self, topic, message):
        self.client.publish(topic, message)


def main():
    wlan = networking.get_wlan()
    # need a current time to communicate with Azure
    ntptime.settime()

    azure_config = az_client.get_azure_config()

    dm = DirectMethodHandler()
    az = AzureClient(dm)

    # Wait for connect or fail
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    # Handle connection error
    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print('ip = ' + status[0])
        try:
            az.connect(azure_config)
        except OSError as e:
            az.reconnect()

    clientid = azure_config.deviceid
    topic_pub = bytes(f'devices/{clientid}/messages/events/', "utf-8")
    while True:
        az.process()

        if button.value():
            az.publish(topic_pub, topic_msg)
            time.sleep(0.5)
        else:
            pass
