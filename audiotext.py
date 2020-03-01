import json
from gtts import gTTS
from playsound import playsound

AUDIOTEXT = "textspeech.json"
AUDIOFILES = "audio"

# audio stuff

def _audio_path(name):
    return f'{AUDIOFILES}/{name}.mp3'

def create_audio():
    '''creates audio files'''
    with open(AUDIOTEXT) as f:
        print(f.read())
        for name, speech in json.load(f).items():
            tts = gTTS(speech)
            tts.save(_audio_path(name))

def play(name):
    playsound(_audio_path(name))

