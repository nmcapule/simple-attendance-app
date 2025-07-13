// Camera and attendance submission for employees
document.addEventListener("DOMContentLoaded", function () {
  const video = document.getElementById("video");
  const canvas = document.getElementById("canvas");
  const captureBtn = document.getElementById("capture");
  const resultDiv = document.getElementById("result");

  // Access camera
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then((stream) => {
      video.srcObject = stream;
    })
    .catch((err) => {
      resultDiv.textContent = "Camera access denied.";
    });

  function showLoadingIndicator() {
    // Hide camera and button
    video.style.display = "none";
    captureBtn.parentElement.style.display = "none";
    // Show result
    resultDiv.style.display = "block";
    resultDiv.textContent = "Submitting attendance...";
  }

  function redirectToResult({ status, employee_id, message }) {
    const params = new URLSearchParams();
    if (status) params.append("status", status);
    if (employee_id) params.append("employee_id", employee_id);
    if (message) params.append("message", message);
    window.location.href = `/result?${params.toString()}`;
  }

  captureBtn.onclick = function () {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    showLoadingIndicator(); // Show loading indicator
    canvas.toBlob(function (blob) {
      const formData = new FormData();
      formData.append("image", blob, "attendance.jpg");
      fetch("/submit_attendance", {
        method: "POST",
        body: formData,
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.status === "success") {
            redirectToResult({
              status: "success",
              employee_id: data.employee_id,
            });
          } else {
            redirectToResult({ status: "fail", message: data.message });
          }
        })
        .catch(() => {
          redirectToResult({
            status: "fail",
            message: "Error submitting attendance.",
          });
        });
    }, "image/jpeg");
  };
});
