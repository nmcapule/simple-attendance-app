// Camera and attendance submission for employees
document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const captureBtn = document.getElementById('capture');
    const resultDiv = document.getElementById('result');

    // Access camera
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => { video.srcObject = stream; })
        .catch(err => { resultDiv.textContent = 'Camera access denied.'; });

    captureBtn.onclick = function() {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        canvas.toBlob(function(blob) {
            const formData = new FormData();
            formData.append('image', blob, 'attendance.jpg');
            fetch('/submit_attendance', {
                method: 'POST',
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    resultDiv.textContent = 'Attendance submitted! Employee ID: ' + data.employee_id;
                } else {
                    resultDiv.textContent = data.message;
                }
            })
            .catch(() => { resultDiv.textContent = 'Error submitting attendance.'; });
        }, 'image/jpeg');
    };
});
