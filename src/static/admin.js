// Admin registration: upload or camera

document.addEventListener("DOMContentLoaded", function () {
  const openCameraBtn = document.getElementById("openCamera");
  const adminVideo = document.getElementById("adminVideo");
  const adminCanvas = document.getElementById("adminCanvas");
  const registerForm = document.getElementById("registerForm");
  const adminResult = document.getElementById("adminResult");
  let stream = null;

  openCameraBtn.onclick = function () {
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then((s) => {
        stream = s;
        adminVideo.srcObject = stream;
        adminVideo.style.display = "block";
      })
      .catch(() => {
        adminResult.textContent = "Camera access denied.";
      });
  };

  registerForm.onsubmit = function (e) {
    e.preventDefault();
    const nickname = registerForm.nickname.value;
    let imageFile = registerForm.image.files[0];
    if (adminVideo.style.display === "block") {
      adminCanvas.width = adminVideo.videoWidth;
      adminCanvas.height = adminVideo.videoHeight;
      adminCanvas.getContext("2d").drawImage(adminVideo, 0, 0);
      adminCanvas.toBlob(function (blob) {
        submitRegistration(nickname, blob);
      }, "image/jpeg");
    } else if (imageFile) {
      submitRegistration(nickname, imageFile);
    } else {
      adminResult.textContent = "Please provide an image.";
    }
  };

  function submitRegistration(nickname, imageBlob) {
    const formData = new FormData();
    formData.append("nickname", nickname);
    formData.append("image", imageBlob, "employee.jpg");
    fetch("/register_employee", {
      method: "POST",
      body: formData,
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.status === "success") {
          adminResult.textContent =
            "Employee registered! Nickname: " + data.nickname;
        } else {
          adminResult.textContent = data.message;
        }
      })
      .catch(() => {
        adminResult.textContent = "Error registering employee.";
      });
  }
});
