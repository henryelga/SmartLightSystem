import RPi.GPIO as GPIO
import time, os
import json

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener
from dotenv import load_dotenv

# PubNub setup
app_channel = "elgas_pi_channel"
data = {}
load_dotenv()

manual_light_on = False
last_event_time = 0  # Tracks last detected event time

# PubNub listener
class Listener(SubscribeListener):
    def status(self, pubnub, status):
        print(f'Status: \n{status.category.name}')

# Configure PubNub
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

# GPIO pin setup
PIR_pin = 23           # Motion Sensor
LED_pin = 24           # LED
BEAM_pin = 17          # IR Break Beam Sensor

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_pin, GPIO.IN)
GPIO.setup(LED_pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(BEAM_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Handle incoming PubNub messages
def handle_message(message):
    global manual_light_on, last_event_time
    msg = message.message  # Directly use the message (already in JSON format)

    # Handle LED control
    if 'lights' in msg:
        if msg['lights'] == 'off':
            GPIO.output(LED_pin, False)
            manual_light_on = False
            print("LED turned off")
        elif msg['lights'] == 'on':
            GPIO.output(LED_pin, True)
            manual_light_on = True
            last_event_time = time.time()
            print("LED turned on")

# Motion and IR detection loop
def detection_loop():
    global last_event_time, manual_light_on

    light_on_duration = 10  # Keep light on for 10 seconds after last event

    while True:
        motion_detected = GPIO.input(PIR_pin)  # Motion Sensor
        beam_broken = GPIO.input(BEAM_pin) == 0  # IR Beam Sensor

        # Both Motion and Beam Broken
        if motion_detected and beam_broken:
            last_event_time = time.time()
            print("Motion Detected and IR Beam Broken")
            GPIO.output(LED_pin, True)
            pubnub.publish().channel(app_channel).message({"Motion": "Yes"}).sync()
            pubnub.publish().channel(app_channel).message({"Beam": "Broken"}).sync()

        # Only Motion Detected
        if motion_detected:
            last_event_time = time.time()
            print("Motion Detected")
            GPIO.output(LED_pin, True)
            pubnub.publish().channel(app_channel).message({"Motion": "Yes"}).sync()

        # Only Beam Broken
        if beam_broken:
            last_event_time = time.time()
            print("IR Beam Broken")
            GPIO.output(LED_pin, True)
            pubnub.publish().channel(app_channel).message({"Beam": "Broken"}).sync()

        #if not motion_detected:
         #   print("No Motion Detected")
          #  pubnub.publish().channel(app_channel).message({"Motion": "Yes"}).sync()
	#	time.sleep(0.5)

        if not beam_broken:
            print("IR Beam Not Broken")
            pubnub.publish().channel(app_channel).message({"Beam": "Not broken"}).sync()
		time.sleep(0.5)


        # Turn off LED if no event happens within duration
        if not manual_light_on and time.time() - last_event_time > light_on_duration:
            GPIO.output(LED_pin, False)
            pubnub.publish().channel(app_channel).message({"Motion": "No"}).sync()
            pubnub.publish().channel(app_channel).message({"Beam": "Not broken"}).sync()

        time.sleep(0.5)

def main():
    detection_loop()

if __name__ == "__main__":
    main()
