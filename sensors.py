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
last_motion = 0

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
IR1_pin = 17           # IR Break Beam Sensor 1 (Receiver White Wire)
IR2_pin = 27           # IR Break Beam Sensor 2 (Receiver White Wire)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_pin, GPIO.IN)
#GPIO.setup(LED_pin, GPIO.OUT)
GPIO.setup(LED_pin, GPIO.OUT, initial=GPIO.LOW)  # Set LED OFF initially
GPIO.setup(IR1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up resistor for IR1
GPIO.setup(IR2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up resistor for IR2

# Handle incoming PubNub messages
def handle_message(message):
    global manual_light_on, last_motion
    msg = json.loads(json.dumps(message.message))
    
    # Handle LED control
    if 'lights' in msg:
        if msg['lights'] == 'off':
            GPIO.output(LED_pin, False)
            manual_light_on = False
            print("LED turned off")
        elif msg['lights'] == 'on':
            GPIO.output(LED_pin, True)
            manual_light_on = True
            last_motion = time.time()
            print("LED turned on")

# Motion and IR detection loop
def detection_loop():
    global last_motion, manual_light_on

    light_on_duration = 10  # seconds

    while True:
        # Motion Sensor Detection
        if GPIO.input(PIR_pin):
            last_motion = time.time()
            print("Motion Detected")
            GPIO.output(LED_pin, True)
            manual_light_on = False
            pubnub.publish().channel(app_channel).message('"Motion":"Yes"').sync()

        # IR Break Beam Sensor 1
        if GPIO.input(IR1_pin) == 0:  # Beam is broken
            print("IR Sensor 1 Beam Broken")
            GPIO.output(LED_pin, True)
            pubnub.publish().channel(app_channel).message('"IR1_Beam":"Broken"').sync()
            time.sleep(1)

        # IR Break Beam Sensor 2
        if GPIO.input(IR2_pin) == 0:  # Beam is broken
            print("IR Sensor 2 Beam Broken")
            GPIO.output(LED_pin, True)
            pubnub.publish().channel(app_channel).message('"IR2_Beam":"Broken"').sync()
            time.sleep(1)

        # Turn off LED if no motion or manual override
        if not manual_light_on and time.time() - last_motion > light_on_duration:
            GPIO.output(LED_pin, False)
            pubnub.publish().channel(app_channel).message('"Motion":"No"').sync()

        time.sleep(0.5)

def main():
    detection_loop()

if __name__ == "__main__":
    main()
