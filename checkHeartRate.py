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
import json
from google.cloud import pubsub
from oauth2client.client import GoogleCredentials
import RPi.GPIO as io # import the GPIO library we just installed but call it "io"

SAMPLE_COUNT_THRESHOLD = 10
 
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
    # firstBeatTime = time.time()
    totalSampleCounter = 0
    sampleCounter = 0

    while True:
        # if sampleCounter == 0: 
        #    firstBeatTime = time.time()
        #    print "firstBeatTime: " + str(firstBeatTime)

        ## inputReceived will either be 1 or 0
        inputReceived = io.input(receiver_in)

        if inputReceived == 1 and previousInput == 0:
            # io.output(LED_in, io.LOW) # turn LED on
            previousInput = inputReceived
            if totalSampleCounter == 0:
                totalSampleCounter = 1
                firstBeatTime = time.time()
            else:
                totalSampleCounter = totalSampleCounter + 1
                sampleCounter = sampleCounter + 1
            # print "Total beats: " + str(totalSampleCounter) + ", current samples: " + str(sampleCounter)
            if sampleCounter == SAMPLE_COUNT_THRESHOLD:
                sampleCounter = 0 # reset the sample counter

                # calculate beats per minute given the SAMPLE_COUNT
                sampleSeconds = time.time() - firstBeatTime
                # print 'Sample Seconds: ' + str(sampleSeconds)
                sampleSecondsPerBeat = sampleSeconds/SAMPLE_COUNT_THRESHOLD
               	# print 'Sample Seconds Per Beat: ' + str(sampleSecondsPerBeat)
                bpm = 60/sampleSecondsPerBeat

                # show beats per minute
                currentBPM = str(bpm) + ' bpm'
                print currentBPM

                firstBeatTime = time.time()

        elif inputReceived == 1 and previousInput == 1:
            previousInput = inputReceived
        else:
            io.output(LED_in, io.HIGH) # turn LED off
          
            # Set the previous sample to the current sample so that it can be used to
            # evaluate if at the front edge of the heartbeat and not count it more than
            # once if already in the high position          
            previousInput = inputReceived


## this allows you to end the script with ctrl+c
except Exception as e:
    print "There was an error"
    print (e)
