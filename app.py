from flask import Flask, render_template, request, redirect, url_for, jsonify
from deepface import DeepFace
import os

app = Flask(__name__, template_folder="src/templates", static_folder="src/static")
app.config["UPLOAD_FOLDER"] = "src/static/uploads"

# In-memory employee database (for demo)
employees = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/submit_attendance", methods=["POST"])
def submit_attendance():
    # Handle image upload and face verification
    image = request.files.get("image")
    if image:
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
        image.save(image_path)
        # Compare with registered employees
        for emp_id, emp_img in employees.items():
            try:
                result = DeepFace.verify(image_path, emp_img)
                if result["verified"]:
                    return jsonify({"status": "success", "employee_id": emp_id})
            except Exception as e:
                continue
        return jsonify({"status": "fail", "message": "No match found"})
    return jsonify({"status": "fail", "message": "No image uploaded"})


@app.route("/register_employee", methods=["POST"])
def register_employee():
    emp_id = request.form.get("employee_id")
    image = request.files.get("image")
    if emp_id and image:
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
        image.save(image_path)
        employees[emp_id] = image_path
        return jsonify({"status": "success", "employee_id": emp_id})
    return jsonify({"status": "fail", "message": "Missing data"})


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.run(debug=True)
