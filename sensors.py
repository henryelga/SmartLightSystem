import RPi.GPIO as GPIO
import time, os
import json

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener
from dotenv import load_dotenv

app_channel = "elgas_pi_channel"

data = {}

load_dotenv()

manual_light_on = False
last_motion = 0

class Listener(SubscribeListener):
    def status(self, pubnub, status):
        print(f'Status: \n{status.category.name}')

config = PNConfiguration()
config.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
config.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
config.user_id = "raspberry_pi"

pubnub = PubNub(config)
pubnub.add_listener(Listener())

subscription = pubnub.channel(app_channel).subscription()
subscription.on_message = lambda message: handle_message(message)
subscription.subscribe()

time.sleep(1)

def handle_message(message):

    global manual_light_on, last_motion
    msg = json.loads(json.dumps(message.message))
        
    # check for 'lights' in the message and handle LED control
    if 'lights' in msg:
        #print(msg)
        #print(msg['lights'])
        if msg['lights'] == 'off':
            GPIO.output(LED_pin, False)  # turn off the LED
            manual_light_on = False
            print("LED turned off")
        elif msg['lights'] == 'on':
            GPIO.output(LED_pin, True)   # turn on the LED
            manual_light_on = True
            last_motion = time.time()
            print("LED turned on")


publish_result = pubnub.publish().channel(app_channel).message('Hello from Elgas Pi').sync()

PIR_pin = 23
LED_pin = 24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_pin, GPIO.IN)
#GPIO.setup(Buzzer_pin, GPIO.OUT)
GPIO.setup(LED_pin, GPIO.OUT)

def motion_detection():

    global last_motion, manual_light_on

    light_on_duration = 10 # in seconds
  
    while True:
        if GPIO.input(PIR_pin):
            last_motion = time.time() # set motion detected time
            print("Motion Detected")
            GPIO.output(LED_pin, True)
            manual_light_on = False
            pubnub.publish().channel(app_channel).message('"Motion":"Yes"').sync()

        if not manual_light_on and time.time() - last_motion > light_on_duration: # check if led should still be on
            GPIO.output(LED_pin, False) 
            pubnub.publish().channel(app_channel).message('"Motion":"No"').sync()

        time.sleep(1)

def main():
    motion_detection()

if __name__ == "__main__":
    main()
