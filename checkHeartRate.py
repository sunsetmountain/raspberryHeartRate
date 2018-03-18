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
credentials = GoogleCredentials.get_application_default()
# change project to your Project ID
project="codelab-testing"
# change topic to your PubSub topic name
topic = "heartratedata"
# set the following four constants to be indicative of where you are placing your weather sensor
sensorID = "s-testing"

SAMPLE_COUNT_THRESHOLD = 10
 
## set GPIO mode to BCM -- this takes GPIO number instead of pin number
io.setmode(io.BCM)
io.setwarnings(False)
 
receiver_in = 23 # this is the GPIO number our receiver is connected to

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

def monitorForPulse():
    ## this try block looks for 1 values (indicate a beat) from the transmitter
    try:
        # firstBeatTime = time.time()
        totalSampleCounter = 0
        sampleCounter = 0

        while True:
            ## inputReceived will either be 1 or 0
            inputReceived = io.input(receiver_in)

            if inputReceived == 1 and previousInput == 0:
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
                    currentTime = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    heartrateJSON = createJSON(sensorID, currentTime, currentBPM)
                    publish_message(project, topic, heartrateJSON)
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


def main():

    io.setup(receiver_in, io.IN) # initialize receiver GPIO to take input
    
    ## indicate that everything is ready to receive the heartbeat signal
    print "Waiting for heartbeat"
    monitorForPulse()

if __name__ == '__main__':
	   main()
   
