import RPi.GPIO as GPIO
import time
import os
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from dotenv import load_dotenv

# PubNub setup
app_channel = "elgas_pi_channel"
load_dotenv()

manual_light_on = False
last_light_status = False
last_event_time = 0  

# Configure PubNub
config = PNConfiguration()
config.subscribe_key = os.getenv("PUBNUB_SUBSCRIBE_KEY")
config.publish_key = os.getenv("PUBNUB_PUBLISH_KEY")
config.user_id = "raspberry_pi"

pubnub = PubNub(config)

# GPIO pin setup
PIR_pin = 23           # Motion Sensor
LED_pin = 24           # LED
BEAM_pin = 17          # IR Break Beam Sensor

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_pin, GPIO.IN)
GPIO.setup(LED_pin, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(BEAM_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Motion and IR detection loop
def detection_loop():
    global last_event_time, manual_light_on, last_light_status

    light_on_duration = 10  # Keep light on for 10 seconds after last event
    motion_state = False  # Tracks the current motion state
    beam_state = False  # Tracks the current beam state

    while True:
        motion_detected = GPIO.input(PIR_pin)  # Motion Sensor
        beam_broken = GPIO.input(BEAM_pin) == 0  # IR Beam Sensor

        # Update last_event_time if there is any motion or beam break
        if motion_detected or beam_broken:
            last_event_time = time.time()

        # Publish motion status only when the state changes
        if motion_detected != motion_state:
            motion_state = motion_detected
            if motion_state:
                print("Motion detected!")
                pubnub.publish().channel(app_channel).message({
                    "event": "motion_detected",
                    "status": "Detected"
                }).sync()
            else:
                print("No motion detected.")
                pubnub.publish().channel(app_channel).message({
                    "event": "motion_detected",
                    "status": "Not detected"
                }).sync()

        # Publish beam status only when the state changes
        if beam_broken != beam_state:
            beam_state = beam_broken
            if beam_state:
                print("Beam broken!")
                pubnub.publish().channel(app_channel).message({
                    "event": "beam_broken",
                    "status": "Broken"
                }).sync()
            else:
                print("Beam not broken.")
                pubnub.publish().channel(app_channel).message({
                    "event": "beam_broken",
                    "status": "Not broken"
                }).sync()

        # Determine if the light should stay on
        time_since_last_event = time.time() - last_event_time
        light_should_be_on = (
            (time_since_last_event <= light_on_duration) or manual_light_on or beam_broken
        )

        # Determine the current light status
        current_light_status = "On" if light_should_be_on else "Off"

        # Update the light based on the current status
        GPIO.output(LED_pin, current_light_status == "On")
        print(f"Light status: {current_light_status}")

        # Publish the light status to PubNub
        if current_light_status != last_light_status:
            last_light_status = current_light_status
            pubnub.publish().channel(app_channel).message({
                "light_status": current_light_status
            }).sync()

        time.sleep(0.5)

def main():
    detection_loop()

if __name__ == "__main__":
    main()
