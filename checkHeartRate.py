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

# constants - change to fit your project and location

project="codelab-testing-198216"  # change project to your Project ID
topic = "heartratedata"  # change topic to your PubSub topic name
sensorID = "s-testing"  # change to a descriptive name for your sensor
heartbeatsToCount = 10 # number of heart beats to sample before calculating BPM
receiver_in = 23 # this is the GPIO number our receiver is connected to
credentials = GoogleCredentials.get_application_default()
 
## set GPIO mode to BCM -- this takes GPIO number instead of pin number
io.setmode(io.BCM)
io.setwarnings(False)

def publish_message(project_name, topic_name, data):
  try:
      publisher = pubsub.PublisherClient()	
      topic = 'projects/' + project_name + '/topics/' + topic_name
      publisher.publish(topic, data, placeholder='')
      print data
  except:
      print "There was an error publishing heartrate data."


def createJSON(id, timestamp, heartrate):
    data = {
      'sensorID' : id,
      'timecollected' : timestamp,
      'heartrate' : heartrate
    }

    json_str = json.dumps(data)
    return json_str

def calcBPM(startTime, endTime):   
    sampleSeconds = endTime - startTime  # calculate time gap between first and last heartbeat
    bpm = (60/sampleSeconds)*(heartbeatsToCount)
    currentTime = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    heartrateJSON = createJSON(sensorID, currentTime, bpm)
    publish_message(project, topic, heartrateJSON)
    time.sleep(5) # wait to allow the message publication process to finish (it can interfere with capturing heart beat signals)

 
def monitorForPulse():
    totalSampleCounter = 0
    sampleCounter = -1
    previousInput = 0
    lastPulseTime = 0
    thisPulseTime = 0
    firstSampleTime = 0
    lastSampleTime = 0
    instantBPM = 0

    ## this try block looks for 1 values (indicate a beat) from the transmitter
    try:

        while True:
            
            inputReceived = io.input(receiver_in) # inputReceived will either be 1 or 0

            if inputReceived == 1:
                if previousInput == 0: # the heart beat signal went from low to high
                    totalSampleCounter = totalSampleCounter + 1
                
                    if sampleCounter == -1: # the first beat received since the counter was reset
                        sampleCounter = 0
                        firstSampleTime = time.time() # set the time to start counting beats
                        lastPulseTime = firstSampleTime
                    else:
                        sampleCounter = sampleCounter + 1
                        thisPulseTime = time.time()
                        instantBPM = 60/(thisPulseTime - lastPulseTime)
                        # print "Total measured beats: " + str(totalSampleCounter) + ", instantBPM: " + str(instantBPM) + ", time: " + str(thisPulseTime)
                        lastPulseTime = thisPulseTime
                        
                    if sampleCounter == heartbeatsToCount: # time to calculate the average BPM
                        sampleCounter = -1 # reset the sample counter
                        lastSampleTime = lastPulseTime # set the time the last beat was detected
                        calcBPM(firstSampleTime, lastSampleTime)
                        
            previousInput = inputReceived


    ## this allows you to end the script with ctrl+c
    except Exception as e:
        print "There was an error"
        print (e)


def main():

    io.setup(receiver_in, io.IN) # initialize receiver GPIO to take input
    
    ## indicate that everything is ready to receive the heartbeat signal
    print "Waiting for heartbeat"
    monitorForPulse()

if __name__ == '__main__':
    main()
   
