console.log("Working...");

const pubnub = new PubNub({
    publishKey: 'pub-c-39055472-ec0b-487f-b2a4-89bfe382a3d2',
    subscribeKey: 'sub-c-efff5b33-2da3-4a60-b6b2-e418b270bb86',
    uuid: "raspberry_pi",
});

const CHANNEL_NAME = "elgas_pi_channel"; 

let currentLightStatus = "Off";

function startListeningForUpdates() {
    console.log("Subscribing to channel:", CHANNEL_NAME);

    pubnub.subscribe({ channels: [CHANNEL_NAME] });

    pubnub.addListener({
        message: (event) => {
            console.log("Received message:", event.message);
    
            const motionDetected = event.message.event === "motion_detected" && event.message.status === "Detected";
            const motionNotDetected = event.message.event === "motion_detected" && event.message.status === "Not detected";
            const beamBroken = event.message.event === "beam_broken" && event.message.status === "Broken";
            const beamNotBroken = event.message.event === "beam_broken" && event.message.status === "Not broken";
            const lightStatus = event.message.light_status; 
    
            // Update UI based on received data
            updateMotionStatus(motionDetected || motionNotDetected);
            updateIRSensorStatus(beamBroken ? "Broken" : beamNotBroken ? "Not Broken" : null);
            
            // Update light status
            if (lightStatus === "On" || lightStatus === "Off") {
                updateLightStatus(lightStatus);
            }
    
            // Send the data to the Flask backend
            sendDataToBackend(motionDetected, beamBroken ? "Broken" : beamNotBroken ? "Not Broken" : null, lightStatus, null);
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
let lastMotionStatus = null;
let debounceTimeout;

function updateMotionStatus(status) {
    const motionStatusElement = document.getElementById("motionStatus");
    if (motionStatusElement) {
        const newStatus = status ? "Motion: Detected" : "Motion: No";
        
        // Debounce logic
        clearTimeout(debounceTimeout);
        debounceTimeout = setTimeout(() => {
            if (lastMotionStatus !== newStatus) {
                lastMotionStatus = newStatus;
                motionStatusElement.textContent = newStatus;
                motionStatusElement.classList.toggle('on', status);
                motionStatusElement.classList.toggle('off', !status);
            }
        }, 300); 
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
        } else if (status === "Not Broken") {
            sensorElement.textContent = "IR Break Beam: Not Broken";
            sensorElement.classList.add('off');
            sensorElement.classList.remove('on');
        }
    }
}

function updateLightStatus(status) {
    const lightStatusElement = document.getElementById("lightStatus");
    if (lightStatusElement) {
        // Only update if the new status is different from the current status
        if (status !== currentLightStatus) {
            currentLightStatus = status; 
            
            if (status === "On") {
                lightStatusElement.textContent = "Light: On";
                lightStatusElement.classList.add('on');
                lightStatusElement.classList.remove('off');
            } else if (status === "Off") {
                lightStatusElement.textContent = "Light: Off";
                lightStatusElement.classList.add('off');
                lightStatusElement.classList.remove('on');
            }
        }
    }
}

function sendDataToBackend(motionDetected, beamStatus, lightStatus, manualControl) {
    // Use the last known light status if lightStatus is null
    const lightStatusToSend = lightStatus !== null ? lightStatus : currentLightStatus;

    fetch('/add_event', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            motion_detected: motionDetected,
            beam_status: beamStatus,
            light_status: lightStatusToSend,
            manual_control: manualControl,
        }),
    })
    .then(response => response.json())
    .then(data => {
        console.log("Event data sent to backend:", data);
        // Update currentLightStatus if lightStatusToSend is not null or undefined
        if (lightStatusToSend !== null) {
            currentLightStatus = lightStatusToSend;
        }
    })
    .catch(error => {
        console.error("Error sending data to backend:", error);
    });
}

// Start listening for updates
startListeningForUpdates();
