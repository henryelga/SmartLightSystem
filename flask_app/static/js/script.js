var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.on('update_status', function(data) {
    updateMotionStatus(data.status);
});

function updateMotionStatus(status) {
    const motionStatusElement = document.getElementById('motion-status');
    motionStatusElement.textContent = status;
}
