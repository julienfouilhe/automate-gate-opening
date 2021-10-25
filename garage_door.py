#!/usr/bin/python3

print('Starting to listen to MQTT')

from RPi import GPIO
import time
import paho.mqtt.client as mqtt
print('Imported library mqtt')
from signal import signal, SIGINT
from sys import exit

GPIO.setmode(GPIO.BCM)

gpio = 17

GPIO.setup(gpio, GPIO.OUT)

is_connected = False
failed_connection = False

client = mqtt.Client("seedbox")

print('Everything is setup')

def cleanup():
  print('Exiting gracefully')
  client.loop_stop()
  client.disconnect()
  is_connected = False
  GPIO.cleanup()

def sigintHandler(signal_received, frame):
    # Handle any cleanup here
    print('SIGINT or CTRL-C detected.')
    cleanup()
    exit(0)

signal(SIGINT, sigintHandler)

def _sleepMicroseconds(microseconds):
  delayInSeconds = microseconds / 1000000
  _delayInSeconds = delayInSeconds / 100
  end = time.time() + delayInSeconds - _delayInSeconds
  while time.time() < end:
      time.sleep(_delayInSeconds)

def pulse(high, low):
  GPIO.output(gpio, GPIO.HIGH)
  _sleepMicroseconds(high)
  GPIO.output(gpio, GPIO.LOW)
  _sleepMicroseconds(low)

def sendCode():
  pulse(348, 348)
  pulse(700, 700)
  pulse(348, 700)
  pulse(348, 348)
  pulse(700, 700)
  pulse(348, 700)
  pulse(348, 348)
  pulse(700, 348)
  pulse(700, 348)
  pulse(700, 700)
  pulse(348, 700)
  pulse(348, 700)
  pulse(348, 10004)

def openGate():
  print('Opening gate')
  for _ in range(0, 40):
    sendCode()
  client.publish("sensor/garage_door", "closed")
  client.publish("sensor/garage_door", "opening")
  time.sleep(12)
  client.publish("sensor/garage_door", "open")
  time.sleep(10)
  client.publish("sensor/garage_door", "closing")
  time.sleep(10)
  client.publish("sensor/garage_door", "closed")

def on_message(client, userdata, message):
  payload = str(message.payload.decode("utf-8"))
  print("message received", payload)
  print("message topic=", message.topic)
  if payload == "OPEN":
    openGate()

def on_connect(client, userdata, flags, rc):
  if rc == 0:
    is_connected = True
    print("Connected to MQTT")
  else:
    print("Failed to connect")
    failed_connection = True

client.on_connect = on_connect
client.on_message = on_message
client.connect("192.168.1.77")
client.loop_start()
client.subscribe("cover/garage_door")

while not is_connected and not failed_connection:
    time.sleep(1)

cleanup()