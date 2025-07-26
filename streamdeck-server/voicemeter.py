import os
from time import sleep

MEDIA_DIR = os.path.join(os.path.dirname(__file__), "..", "media")

HEADPHONES_GAIN_OFFSET = (
    -16.5
)  # wired headphones gain offset to make them the same loudness as wireless headphones
MAIN_MIC_DEVICE = "Strip[0]"  # main mic
COMS_DEVICE = "Strip[6]"  # "Voicemeeter Input" used for discord, zoom, etc.

SLIDER0 = "bus-0"  # wired headphones with headphones_gain_offset
SLIDER1 = "bus-1"  # wireless headphones


def play_audio_to_input(vm, path: str):
    _play_audio(
        vm,
        path,
        a1=False,
        a2=False,
        a3=False,
        a4=False,
        a5=False,
        b1=True,
        b2=True,
        b3=True,
    )


def play_audio_to_output(vm, path: str):
    _play_audio(
        vm,
        path,
        a1=True,
        a2=True,
        a3=True,
        a4=True,
        a5=True,
        b1=False,
        b2=False,
        b3=False,
    )


def _play_audio(
    vm,
    path: str,
    a1: bool,
    a2: bool,
    a3: bool,
    a4: bool,
    a5: bool,
    b1: bool,
    b2: bool,
    b3: bool,
):
    vm.recorder.apply(
        {
            "A1": a1,
            "A2": a2,
            "A3": a3,
            "A4": a4,
            "A5": a5,
            "B1": b1,
            "B2": b2,
            "B3": b3,
        }
    )
    vm.recorder.load(path)
    vm.recorder.play()


def toggle_mute(vm, device):
    mute_status = vm.get(f"{device}.Mute")
    if mute_status:
        filename = "unmute.mp3"
    else:
        filename = "mute.mp3"
    path = os.path.join(MEDIA_DIR, filename)

    play_audio_to_output(vm, path)
    vm.set(f"{device}.Mute", not mute_status)


def toggle_deafen(vm, device):
    deafen_status = vm.get(f"{device}.Mute")
    if deafen_status:
        filename = "undeafen.mp3"
        path = os.path.join(MEDIA_DIR, filename)
        vm.set(f"{device}.Mute", not deafen_status)
        play_audio_to_output(vm, path)
    else:
        filename = "deafen.mp3"
        path = os.path.join(MEDIA_DIR, filename)
        play_audio_to_output(vm, path)
        sleep(0.6)
        vm.set(f"{device}.Mute", not deafen_status)


# mapping target_db to target_percent and interpolating from there to the min/max db range
def _percent_to_db(
    percent: float,
    min_db: float = -50,
    target_db: float = -12,
    max_db: float = 12,
    target_percent: float = 50,
    mute_under_percent: float = 0.01,
    mute_db: float = -60,
):

    percent = max(0.0, min(100.0, percent))

    if percent < mute_under_percent * 100:
        return mute_db

    if percent == target_percent:
        return target_db
    elif percent < target_percent:
        norm = percent / target_percent
        return min_db + norm * (target_db - min_db)
    else:
        norm = (percent - target_percent) / target_percent
        return target_db + norm * (max_db - target_db)


def set_volume(vm, slidernum: int, vol: float):
    gain = _percent_to_db(vol)
    if slidernum == 0:
        vm.apply({SLIDER0: {"gain": gain + HEADPHONES_GAIN_OFFSET}})
        vm.apply({SLIDER1: {"gain": gain}})
    elif slidernum == 1:
        vm.apply({COMS_DEVICE: {"gain": gain}})


def toggle_deafen_A1(vm):
    toggle_deafen(vm, "Bus[0].Mute")


def toggle_deafen_A2(vm):
    toggle_deafen(vm, "Bus[1].Mute")


def toggle_deafen_coms(vm):
    toggle_deafen(vm, COMS_DEVICE)


def toggle_mute_mic(vm):
    toggle_mute(vm, MAIN_MIC_DEVICE)
