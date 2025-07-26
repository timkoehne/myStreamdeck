#!/usr/bin/env python3
import serial
from serial import serialutil
import time
import keyboard
from infi.systray import SysTrayIcon
import paho.mqtt.client as mqtt
import json
import voicemeeterlib
import voicemeter


def onClose(arg):
    global exitCondition
    exitCondition = True
    vm.logout()


def keyDelayPassed(i, j):
    if lastKeyPressTimeMs[int(i)][int(j)] + keyPressDelay < current_milli_time():
        lastKeyPressTimeMs[int(i)][int(j)] = current_milli_time()
        return True
    else:
        print("keydelay not up yet")
        return False


def keyPressed(i, j):
    timeInMs = current_milli_time
    if int(i) == 0 and int(j) == 0 and keyDelayPassed(i, j):
        print(keyboard.press("play/pause media"))
    if int(i) == 0 and int(j) == 1 and keyDelayPassed(i, j):
        print(keyboard.press("previous track"))
    if int(i) == 0 and int(j) == 2 and keyDelayPassed(i, j):
        print(keyboard.press("next track"))
    if int(i) == 0 and int(j) == 3 and keyDelayPassed(i, j):
        pass
    if int(i) == 1 and int(j) == 0 and keyDelayPassed(i, j):
        client = mqtt.Client()
        client.username_pw_set(mqttUser, mqttPass)
        client.connect(brokerAdress, brokerPort)
        print("Connected to MQTT Broker: " + brokerAdress)
        client.publish("shelly/switch/timszimmer/toggle", "", qos=0)
    if int(i) == 1 and int(j) == 1 and keyDelayPassed(i, j):
        client = mqtt.Client()
        client.username_pw_set(mqttUser, mqttPass)
        client.connect(brokerAdress, brokerPort)
        print("Connected to MQTT Broker: " + brokerAdress)
        client.publish("esp/curtain/timszimmer/toggle", "", qos=0)
    if int(i) == 1 and int(j) == 2 and keyDelayPassed(i, j):
        pass
    if int(i) == 1 and int(j) == 3 and keyDelayPassed(i, j):
        pass
    if int(i) == 2 and int(j) == 0 and keyDelayPassed(i, j):
        voicemeter.toggle_deafen_A1(vm)
        pass
    if int(i) == 2 and int(j) == 1 and keyDelayPassed(i, j):
        voicemeter.toggle_deafen_A2(vm)
        pass
    if int(i) == 2 and int(j) == 2 and keyDelayPassed(i, j):
        pass
    if int(i) == 3 and int(j) == 0 and keyDelayPassed(i, j):
        voicemeter.toggle_mute_mic(vm)
        pass
    if int(i) == 3 and int(j) == 1 and keyDelayPassed(i, j):
        voicemeter.toggle_deafen_coms(vm)
        pass
    if int(i) == 3 and int(j) == 2 and keyDelayPassed(i, j):
        pass
    if int(i) == 3 and int(j) == 3 and keyDelayPassed(i, j):
        pass
    print("pressed " + str(i) + " " + str(j))


def keyReleased(i, j):
    print("released " + str(i) + " " + str(j))


# read settings
with open("../settings.json", "r") as file:
    settings = json.loads(file.read())
brokerAdress = settings["brokerAdress"]
brokerPort = settings["brokerPort"]
comport = settings["com"]
mqttUser = settings["mqttUsername"]
mqttPass = settings["mqttPassword"]

numberRows = settings["numberRows"]
numberColumns = settings["numberColumns"]

volumeLevel = [100, 100, 100, 100]
keyPressDelay = 300  # in ms

current_milli_time = lambda: int(round(time.time() * 1000))
lastKeyPressTimeMs = [
    [current_milli_time() for x in range(numberRows)] for y in range(numberColumns)
]

systray = SysTrayIcon("icon.ico", "MyStreamdeck", None, on_quit=onClose)
systray.start()

vm = voicemeeterlib.api("potato", sync=True)
vm.login()

exitCondition = False
while not exitCondition:
    if not comport:
        print("Serialport not found... Waiting...")
        time.sleep(5)
    else:
        try:
            with serial.Serial(comport, 9600) as ser:
                print("Connection established at " + comport)
                while not exitCondition:
                    line = ser.readline().decode("utf-8").strip()
                    if "Volumeslider" in line:
                        slidernum = int(line[13])
                        vol = int(line[16:19])
                        voicemeter.set_volume(vm, slidernum, vol)
                    elif "KeyPressed" in line:
                        i = line[12]
                        j = line[14]
                        keyPressed(i, j)
                    elif "KeyReleased" in line:
                        i = line[13]
                        j = line[15]
                        keyReleased(i, j)
        except serialutil.SerialException:
            print("Connection lost...")
            print("Waiting for reconnect")
            time.sleep(5)
        except KeyboardInterrupt:
            print("\nCtrl+C detected! Exiting...")
            exitCondition = True
