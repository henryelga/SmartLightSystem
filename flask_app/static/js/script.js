console.log("Working...");

const pubnub = new PubNub({
    publishKey: 'pub-c-39055472-ec0b-487f-b2a4-89bfe382a3d2',
    subscribeKey: 'sub-c-efff5b33-2da3-4a60-b6b2-e418b270bb86',
    uuid: "raspberry_pi",
});

const CHANNEL_NAME = "elgas_pi_channel"; // Channel name where the Raspberry Pi publishes messages

function startListeningForUpdates() {
    console.log("Subscribing to channel:", CHANNEL_NAME);

    pubnub.subscribe({ channels: [CHANNEL_NAME] });

    pubnub.addListener({
        message: (event) => {
            console.log("Received message:", event.message);

            // Check for motion or IR sensor data
            if (event.message.Motion !== undefined) {
                updateMotionStatus(event.message.Motion);
            } else if (event.message.Beam !== undefined) {
                updateIRSensorStatus(event.message.Beam);
            } else if (event.message.Light !== undefined) {  
                updateLightStatus(event.message.Light);
            }
        },
        status: (statusEvent) => {
            if (statusEvent.category === "PNConnectedCategory") {
                console.log("Successfully connected to PubNub channel.");
            } else {
                console.warn("PubNub connection status:", statusEvent);
            }
        },
    });
}

// Update motion status
function updateMotionStatus(status) {
    const motionStatusElement = document.getElementById("motionStatus");
    if (motionStatusElement) {
        if (status === "Yes") {
            motionStatusElement.textContent = "Motion: Detected";
            motionStatusElement.classList.add('on');
            motionStatusElement.classList.remove('off');
        } else {
            motionStatusElement.textContent = "Motion: No";
            motionStatusElement.classList.add('off');
            motionStatusElement.classList.remove('on');
        }
    }
}

// Update IR sensor status
function updateIRSensorStatus(status) {
    const sensorElement = document.getElementById("irStatus");
    if (sensorElement) {
        if (status === "Broken") {
            sensorElement.textContent = "IR Break Beam: Broken";
            sensorElement.classList.add('on');
            sensorElement.classList.remove('off');
        } else {
            sensorElement.textContent = "IR Break Beam: Not Broken";
            sensorElement.classList.add('off');
            sensorElement.classList.remove('on');
        }
    }
}

// Update Light status

// Update light status
function updateLightStatus(status) {
    const lightStatusElement = document.getElementById("lightStatus");
    if (lightStatusElement) {
        if (status === "On") {
            lightStatusElement.textContent = "Light: On";
            lightStatusElement.classList.add('on');
            lightStatusElement.classList.remove('off');
        } else {
            lightStatusElement.textContent = "Light: Off";
            lightStatusElement.classList.add('off');
            lightStatusElement.classList.remove('on');
        }
    }
}


// Initialize the subscription and listening for updates
startListeningForUpdates();
