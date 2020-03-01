import time
import json
import os
import subprocess
from shlex import split
from collections import deque
#from google.cloud import texttospeech

OUTFOLDER = "outfile"

class FrameParser:
    MAX_QUEUE_LEN = 10
    
    def __init__(self,n):
        self.n = n
        self.queue = deque()
        self.current_stack = deque()
    
    def add(self,frame):
        self.current_stack.append(frame)

        if len(self.current_stack) == self.n:
            avg_frame = self.calculate_avg()
            self.queue.append(avg_frame)
            self.current_stack.clear()
        
        if len(self.queue) > FrameParser.MAX_QUEUE_LEN:
            self.queue.popleft()
    
    def calculate_avg(self):
        avg = [0 for _ in range(25)]

        for frame in self.current_stack:
            for people in frame["people"]:
                if people["person_id"] == -1:
                    key_points = people["pose_keypoints_2d"]
                    for i, pt in enumerate(key_points):
                        avg[i] += pt
        
        avg = [x/self.n for x in avg]
        return avg
    
    
'''
def text_to_speech_code():
    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.types.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    # Set the text input to be synthesized
    synthesis_input = texttospeech.types.SynthesisInput(text="Hello, World!")

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)
'''

def launch_openpose(): #runs with Windows
    cmd = f"./bin/OpenPoseDemo.exe --write_json {OUTFOLDER} --part_candidates"
    try:
        proc = subprocess.Popen(split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.communicate(timeout=10)
    except subprocess.TimeoutExpired: # wait 10 seconds, maybe make more variable
        pass

def read_out(key_num):
    file_name = f"{OUTFOLDER}/{key_num:012d}_keypoints.json"
    print(f"Reading file {file_name}")
    with open(file_name, "r") as f:
        json_obj = json.load(f)
    os.remove(file_name)
    return json_obj
    
def read_loop(fp):
    i = 0
    max_fails, fail_count = 5, 0
    while True:
        try:
            json_object = read_out(i)
            fp.add(json_object)
            i += 1
            fail_count = 0
        except FileNotFoundError:
            if fail_count == max_fails: break
            else:
                fail_count += 1
                print(f'the race is on!!')
                time.sleep(1) # wait a bit


if __name__ == "__main__":
    fp = FrameParser(10)
    launch_openpose()
    read_loop(fp)


