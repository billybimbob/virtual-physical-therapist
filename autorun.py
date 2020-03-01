import json
import math
import time

import os
import subprocess
from shlex import split

import audiotext
from collections import deque

OUTFOLDER = "outfiles"

class FrameParser:
    MAX_QUEUE_LEN = 10
    BODYPOINTS = 25
    NUMELEMs = 3
    VALS = 1
    
    def __init__(self,n=MAX_QUEUE_LEN):
        self.n = n
        self.queue = deque()
        self.current_stack = deque()
    
    def calculate_avg(self):
        indices = FrameParser.VALS * FrameParser.NUMELEMs
        avg = [[0 for _ in range(indices)] for _ in range(FrameParser.BODYPOINTS)]
        for frame in self.current_stack: # only look at first 3 vals
            for part_idx, pt_lst in frame["part_candidates"][0].items():
                pn = int(part_idx)
                for i, pt in zip(range(3), pt_lst):
                    avg[pn][i] += pt
        return [[x/self.n for x in lst] for lst in avg]

    def add(self,frame):
        self.current_stack.append(frame)
        if len(self.current_stack) == self.n:
            avg_bod = self.calculate_avg()
            self.queue.append(avg_bod)
            self.current_stack.clear()
        
        if len(self.queue) > FrameParser.MAX_QUEUE_LEN:
            self.queue.popleft()

        return avg_bod
    
    
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
    inward = True # curl to start
    while True:
        try:
            json_object = read_out(i)
            avgs = fp.add(json_object)
            i += 1
            fail_count = 0
            if avgs is not None:
                check_curl(avgs, inward)
                inward = not inward
        except FileNotFoundError:
            if fail_count == max_fails: break
            else:
                fail_count += 1
                audiotext.play('fail')
                time.sleep(0.5) # wait a bit

# checks

def create_avgvec(avgs, bidx1, bidx2):
    '''
    creates a vector from p2 to p1, where
    idx 0 is x and 1 is y
    '''
    p1, p2 = avgs[bidx1:bidx1+2], avgs[bidx2:bidx2+2]
    return (p2[0]-p1[0], p2[1]-p1[1])

def angle(v1, v2): #could use numpy
    def dotproduct(v1, v2):
        return sum((a*b) for a, b in zip(v1, v2))
    def length(v):
        return math.sqrt(dotproduct(v, v))

    return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))

def rotate_check(v1, v2, inward=True):
    angle_val = math.degrees(angle(v1, v2))
    return angle_val < 30 if inward \
    else   angle_val > 90

def check_curl(avg, inward=True):
    joint_checks = [(2, 3, 4), (5, 6, 7), (9, 10, 11), (12, 13, 14)] # all curl joints
    # check if one in correct position, keep eye on
    for idxs in joint_checks:
        passed = rotate_check( # v1 = 0 to 1, v2 = 1 to 2
            create_avgvec(avg, idxs[0], idxs[1]),
            create_avgvec(avg, idxs[1], idxs[2]),
            inward
        )
        if passed: break
    else:
        audiotext.play('wrong')
        return
    audiotext.play('congrats')


if __name__ == "__main__":
    audiotext.create_audio()
    fp = FrameParser()
    #launch_openpose()
    read_loop(fp)



