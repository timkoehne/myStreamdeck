#!/usr/bin/env python3
import serial
import serial.tools.list_ports
import time
import keyboard
from AudioController import AudioProcessController, AudioDeviceController
from infi.systray import SysTrayIcon
import paho.mqtt.client as mqtt
import json

def createVolumeSliderFromSetting(volumeSliderIndex: int):
    setting = settings["volumeSlider" + str(volumeSliderIndex)]
    if setting == "master":
        return setting
    else:
        return AudioProcessController(setting)

def onClose(arg):
    global exitCondition
    exitCondition = True

def setVolume(slidernum, vol):
    volumeLevel[int(slidernum)] = vol
    if volumeSlider[int(slidernum)] is not None:
        if volumeSlider[int(slidernum)] == "master":
            defaultDeviceEndpoint.setVolume(vol)
        else:
            volumeSlider[int(slidernum)].set_volume(vol)

def keyDelayPassed(i, j):
    if lastKeyPressTimeMs[int(i)][int(j)] + keyPressDelay < current_milli_time():
        lastKeyPressTimeMs[int(i)][int(j)] = current_milli_time()
        return True
    else:
        print("keydelay not up yet")
        return False
            
def keyPressed(i, j):
        timeInMs = current_milli_time
        if int(i)==0 and int(j)==0 and keyDelayPassed(i, j):
            print(keyboard.press("play/pause media"))
        if int(i)==0 and int(j)==1 and keyDelayPassed(i, j):
            print(keyboard.press("previous track"))
        if int(i)==0 and int(j)==2 and keyDelayPassed(i, j):
            print(keyboard.press("next track"))
        if int(i)==0 and int(j)==3 and keyDelayPassed(i, j):
            pass
        if int(i)==1 and int(j)==0 and keyDelayPassed(i, j):
            client = mqtt.Client()
            client.connect(brokerAdress, brokerPort)
            print("Connected to MQTT Broker: " + brokerAdress)
            client.publish("shelly/switch/timszimmer/toggle", "", qos=0)
        if int(i)==1 and int(j)==1 and keyDelayPassed(i, j):
            client = mqtt.Client()
            client.connect(brokerAdress, brokerPort)
            print("Connected to MQTT Broker: " + brokerAdress)
            client.publish("esp/curtain/timszimmer/toggle", "", qos=0)
        if int(i)==1 and int(j)==2 and keyDelayPassed(i, j):
            pass
        if int(i)==1 and int(j)==3 and keyDelayPassed(i, j):
            pass
        if int(i)==2 and int(j)==0 and keyDelayPassed(i, j):
            pass
        if int(i)==2 and int(j)==1 and keyDelayPassed(i, j):
            pass
        if int(i)==2 and int(j)==2 and keyDelayPassed(i, j):
            pass
        if int(i)==3 and int(j)==0 and keyDelayPassed(i, j):
            #mute/unmute myself
            keyboard.send("f13")  #discord and zoom
        if int(i)==3 and int(j)==1 and keyDelayPassed(i, j):
            #deafen/undeafen
            keyboard.send("f14") #discord
            #AudioProcessController("zoom.exe").toggle_mute()
            pass
        if int(i)==3 and int(j)==2 and keyDelayPassed(i, j):
            #show/hide video in zoom
            keyboard.send("f15")
            pass
        if int(i)==3 and int(j)==3 and keyDelayPassed(i, j):
            #raise hand in zoom
            keyboard.send("f16")
            pass
        print("pressed " + str(i) + " " + str(j))
        
def keyReleased(i, j):
    print("released " + str(i) + " " + str(j))

#read settings                
with open("../settings.json", "r") as file:
    settings = json.loads(file.read())
brokerAdress = settings["brokerAdress"]
brokerPort = settings["brokerPort"]
comport = settings["com"]
numberVolumeSliders =  len([key for key in list(settings.keys()) if "volumeSlider" in str(key)])
volumeSlider = [createVolumeSliderFromSetting(i) for i in range(4)]
numberRows = settings["numberRows"]
numberColumns = settings["numberColumns"]

volumeLevel = [100,100,100,100]
keyPressDelay = 300 #in ms

current_milli_time = lambda: int(round(time.time() * 1000))
lastKeyPressTimeMs = [[current_milli_time() for x in range(numberRows)] for y in range(numberColumns)] 

systray = SysTrayIcon("icon.ico", "MyStreamdeck", None, on_quit=onClose)
systray.start()

exitCondition = False
defaultDeviceEndpoint = AudioDeviceController()
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
                        slidernum = line[13]
                        vol = int(line[16:19])
                        setVolume(slidernum, vol)
                    elif "KeyPressed" in line:
                        i = line[12]
                        j = line[14]
                        keyPressed(i, j)
                    elif "KeyReleased" in line:
                        i = line[13]
                        j = line[15]
                        keyReleased(i, j)
        except serial.serialutil.SerialException:
                print("Connection lost...")
                print("Waiting for reconnect")
                time.sleep(5)
