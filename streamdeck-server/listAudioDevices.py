from pycaw.pycaw import AudioUtilities
from pycaw.pycaw import AudioDeviceState

for device in AudioUtilities.GetAllDevices():
    if device.state is AudioDeviceState.Active:
        print(str(device)[13:])