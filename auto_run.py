import json
import math

import time
import os
import subprocess
from shlex import split

from collections import deque
from gtts import gTTS
from playsound import playsound

OUTFOLDER = "outfile"

class FrameParser:
    MAX_QUEUE_LEN = 10
    
    def __init__(self,n=MAX_QUEUE_LEN):
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
        avg = [[0 for _ in range(3)] for _ in range(25)] #only look at first 3 vals
        for frame in self.current_stack:
            for part_idx, pt_lst in frame["part_candidates"][0].items():
                pn = int(part_idx)
                for i, pt in zip(range(3), pt_lst):
                    avg[pn][i] += pt
                    
        avg = [[x/self.n for x in lst] for lst in avg]
        return avg
    
    
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
                fail()
                print(f'the race is on!!')
                time.sleep(1) # wait a bit

def fail():
    '''creates audio file'''
    try:
        tts = gTTS('The race is on!!')
        tts.save('audio/Fail.mp3')
    except PermissionError:
        pass
    playsound('audio/Fail.mp3')

def angle(v1, v2):
    def dotproduct(v1, v2):
        return sum((a*b) for a, b in zip(v1, v2))

    def length(v):
        return math.sqrt(dotproduct(v, v))

    return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))


def rotate_check(v1, v2, inward=True):
    angle_val = math.degrees(angle(v1, v2))
    return angle_val < 30 if inward \
    else   angle_val > 90


if __name__ == "__main__":
    fp = FrameParser()
    launch_openpose()
    read_loop(fp)



