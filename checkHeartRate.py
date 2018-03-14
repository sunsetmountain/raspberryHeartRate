# Copyright 2018 Google LLC
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     https://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#!/usr/bin/python

import time
import datetime
import json
from google.cloud import pubsub
from oauth2client.client import GoogleCredentials
import RPi.GPIO as io # import the GPIO library we just installed but call it "io"

SAMPLE_COUNT = 10
 
## set GPIO mode to BCM
## this takes GPIO number instead of pin number
io.setmode(io.BCM)
io.setwarnings(False)
 
receiver_in = 23 # this is the GPIO number our receiver is connected to
LED_in = 24 # GPIO number the LED is connected to
 
io.setup(receiver_in, io.IN) # initialize receiver GPIO to take input
io.setup(LED_in, io.OUT) # initialized LED GPIO to give output
 
io.output(LED_in, io.HIGH) # start with LED off
 
## indicate that everything is ready to receive the heartbeat signal
print "Waiting for heartbeat"
 
## this try block looks for 1 values (indicate a beat) from the transmitter
try:
    firstBeatTime = time.time()
    sampleCounter = 0
    while True:
        if sampleCounter == 0: 
            firstBeatTime = time.time()

        ## sample will either be 1 or 0
        sample = io.input(receiver_in)

        if sample == 1:
            io.output(LED_in, io.LOW) # turn LED on
            sampleCounter = sampleCounter + 1
            if sampleCounter == SAMPLE_COUNT:
                sampleCounter = 0 # reset the sample counter

                # calculate beats per minute given the SAMPLE_COUNT
                sampleMinutes = (time.time() - firstBeatTime)/60
                bpm = sampleMinutes * SAMPLE_COUNT

                # show beats per minute
                currentBPM = bpm + ' bpm'
                print currentBPM
        else:
            io.output(LED_in, io.HIGH) # turn LED off
 
        # Set the previous sample to the current sample so that it can be used to
        # evaluate if at the front edge of the heartbeat and not count it more than
        # once if already in the high position
        previousSample = sample
## this allows you to end the script with ctrl+c
except:
    print "There was an error"
