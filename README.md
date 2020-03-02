# Virtual Physical Therapist

An audio-feedback based virtual tool to help ensure correct physical therapy 
exercises for recovery.

## Implementation

This program is built upon the library, [OpenPose](https://github.com/CMU-Perceptual-Computing-Lab/openpose)
in order to identify body parts and joint for analysis.

OpenPose generates `.json` files, which are read to provide audio feedback 
and assurance. Currently this application utilizes a pre-built demo version of
OpenPose for Windows, and launches a terminal process of this demo version.