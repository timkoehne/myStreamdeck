from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import comtypes
from ctypes import POINTER, cast
import time
from pycaw.constants import (DEVICE_STATE, STGM, AudioDeviceState,
                             CLSID_MMDeviceEnumerator, EDataFlow, ERole,
                             IID_Empty)
from pycaw.api.mmdeviceapi import IMMDeviceEnumerator


class AudioDeviceController(object):

    @staticmethod
    def __getAllIMMDevices():
        devices = []
        deviceEnumerator = comtypes.CoCreateInstance(
            CLSID_MMDeviceEnumerator,
            IMMDeviceEnumerator,
            comtypes.CLSCTX_INPROC_SERVER)
        if deviceEnumerator is None:
            return devices

        collection = deviceEnumerator.EnumAudioEndpoints(
            EDataFlow.eAll.value, DEVICE_STATE.MASK_ALL.value)
        if collection is None:
            return devices

        count = collection.GetCount()
        for i in range(count):
            dev = collection.Item(i)
            if dev is not None:
                devices.append(dev)
        return devices

    @staticmethod
    def __getDefaultDeviceEndpoint():
        return AudioDeviceController.__getVolumeControlFromIMMDevice(AudioUtilities.GetSpeakers())
        
    @staticmethod
    def __getImmDeviceFromPycawDeviceById(id, immDevices):
        for device in immDevices:
            if device.GetId() == id:
                return device
                
    @staticmethod
    def __findAudioDeviceEndpoint(name):
        pycawDevices = AudioUtilities.GetAllDevices()
        immDevices = AudioDeviceController.__getAllIMMDevices()
    
        for device in pycawDevices:
            if device.state.value is AudioDeviceState.Active.value and name == device.FriendlyName:
                    return AudioDeviceController.__getVolumeControlFromIMMDevice(
                        AudioDeviceController.__getImmDeviceFromPycawDeviceById(device.id, immDevices))
    
    @staticmethod
    def __getVolumeControlFromIMMDevice(device):
        interface = device.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        endpoint = cast(interface, POINTER(IAudioEndpointVolume))
        return endpoint    

    def __init__(self, deviceName=None):
        if isinstance(deviceName, str):
            self.endpoint = AudioDeviceController.__findAudioDeviceEndpoint(deviceName)
            print(f"{deviceName}: {self.endpoint}")
        elif deviceName is None:
            self.endpoint = AudioDeviceController.__getDefaultDeviceEndpoint()

    def setMute(self, mute):
        self.endpoint.SetMute(mute)
        
    def getMute(self, mute):
        return self.endpoint.GetMute()

    def setVolume(self, percent):
        self.endpoint.SetMasterVolumeLevelScalar(float(percent/100.0), None)
        
    def getVolume(self):
        return int(round(self.endpoint.GetMasterVolumeLevelScalar() * 100))
        
class AudioProcessController(object):
    def __init__(self, process_names_arr):
        self.process_names = process_names_arr
        for process_name in self.process_names:
            process_name = process_name.lower()
    def listAllSessions(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process:
                print(session.Process)
    def mute(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name().lower() in self.process_names:
                session.SimpleAudioVolume.SetMute(1, None)
    def unmute(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name().lower() in self.process_names:
                session.SimpleAudioVolume.SetMute(0, None)
    def get_mute(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name().lower() in self.process_names:
                if session.SimpleAudioVolume.GetMute():
                    return True
        return False
    def toggle_mute(self):
        if self.get_mute():
            self.unmute()
        else:
            self.mute()
    def get_volume(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name().lower() in self.process_names:
                return session.SimpleAudioVolume.GetMasterVolume()
    def set_volume(self, percent):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.Process.name().lower() in self.process_names:
                session.SimpleAudioVolume.SetMasterVolume(percent/100, None)
