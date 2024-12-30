import RPi.GPIO as GPIO
import time
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener
from dotenv import load_dotenv

# Load environment variables for PubNub keys
load_dotenv()

# PubNub setup
app_channel = "elgas_pi_channel"
config = PNConfiguration()
config.subscribe_key = "sub-c-efff5b33-2da3-4a60-b6b2-e418b270bb86"
config.publish_key = "pub-c-39055472-ec0b-487f-b2a4-89bfe382a3d2"
config.user_id = "raspberry_pi"

pubnub = PubNub(config)

# GPIO pin setup
PIR_pin = 23           # Motion Sensor
LED_pin = 24           # LED
IR1_pin = 17           # IR Break Beam Sensor 1
IR2_pin = 27           # IR Break Beam Sensor 2

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_pin, GPIO.IN)
GPIO.setup(LED_pin, GPIO.OUT, initial=GPIO.LOW)  # Set LED OFF initially
GPIO.setup(IR1_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up resistor for IR1
GPIO.setup(IR2_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Pull-up resistor for IR2

# Manual light status and motion tracking
manual_light_on = False
last_motion = 0
light_on_duration = 10  # seconds

# PubNub Listener class for connection status
class Listener(SubscribeListener):
    def status(self, pubnub, status):
        print(f"Status: {status.category}")
        if status.category == "PNConnectedCategory":
            print("Connected to PubNub!")

    def message(self, pubnub, message):
        print(f"Received message: {message.message}")
        # Handle message (motion or IR beam breakage)
        if 'Motion' in message.message:
            if message.message["Motion"] == "Yes":
                print("Motion detected")
            else:
                print("No motion detected")
        if 'IR1_Beam' in message.message:
            print("IR Sensor 1 Beam Broken")
        if 'IR2_Beam' in message.message:
            print("IR Sensor 2 Beam Broken")

# Subscribe to channel
def subscribe():
    pubnub.add_listener(Listener())
    pubnub.subscribe().channels(app_channel).execute()

# Motion and IR detection loop
def detection_loop():
    global last_motion, manual_light_on

    while True:
        # Motion Sensor Detection
        if GPIO.input(PIR_pin):
            last_motion = time.time()
            print("Motion Detected")
            GPIO.output(LED_pin, True)
            manual_light_on = False
            pubnub.publish().channel(app_channel).message({"Motion": "Yes"}).sync()

        # IR Break Beam Sensor 1
        if GPIO.input(IR1_pin) == 0:  # Beam is broken
            print("IR Sensor 1 Beam Broken")
            GPIO.output(LED_pin, True)
            pubnub.publish().channel(app_channel).message({"IR1_Beam": "Broken"}).sync()
            time.sleep(1)

        # IR Break Beam Sensor 2
        if GPIO.input(IR2_pin) == 0:  # Beam is broken
            print("IR Sensor 2 Beam Broken")
            GPIO.output(LED_pin, True)
            pubnub.publish().channel(app_channel).message({"IR2_Beam": "Broken"}).sync()
            time.sleep(1)

        # Turn off LED if no motion or manual override
        if not manual_light_on and time.time() - last_motion > light_on_duration:
            GPIO.output(LED_pin, False)
            pubnub.publish().channel(app_channel).message({"Motion": "No"}).sync()

        time.sleep(0.5)

# Main function to start the detection loop
def main():
    subscribe()  # Subscribe to PubNub channel
    detection_loop()

if __name__ == "__main__":
    main()
