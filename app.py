from flask import Flask, render_template, request, jsonify, send_from_directory
from deepface import DeepFace
import os
import sqlite3

app = Flask(__name__, template_folder="src/templates", static_folder="src/static")
app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER", "data/uploads")
DATABASE = os.environ.get("DATABASE", "data/attendance.db")


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT NOT NULL,
            image_path TEXT NOT NULL
        )
    """
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            image_path TEXT,
            FOREIGN KEY(employee_id) REFERENCES employees(id)
        )
    """
    )
    conn.commit()
    conn.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")


@app.route("/submit_attendance", methods=["POST"])
def submit_attendance():
    # Handle image upload and face verification
    from datetime import datetime

    image = request.files.get("image")
    if image:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        ext = os.path.splitext(image.filename)[1] or ".jpg"
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id, nickname, image_path FROM employees")
        employees = c.fetchall()
        matched_id = None
        matched_nickname = None
        for emp in employees:
            emp_id = emp["id"]
            emp_nickname = emp["nickname"]
            emp_img = emp["image_path"]
            try:
                temp_filename = f"temp_{timestamp}{ext}"
                temp_path = os.path.join(app.config["UPLOAD_FOLDER"], temp_filename)
                image.save(temp_path)
                result = DeepFace.verify(temp_path, emp_img, model_name="Facenet512")
                if result["verified"]:
                    matched_id = emp_id
                    matched_nickname = emp_nickname
                    break
            except Exception as e:
                continue
        if matched_id:
            final_filename = f"{matched_id}_{timestamp}{ext}"
            final_path = os.path.join(app.config["UPLOAD_FOLDER"], final_filename)
            os.rename(temp_path, final_path)
            c.execute(
                "INSERT INTO attendance (employee_id, image_path) VALUES (?, ?)",
                (matched_id, final_path),
            )
            conn.commit()
            conn.close()
            return jsonify(
                {
                    "status": "success",
                    "employee_id": matched_id,
                    "nickname": matched_nickname,
                }
            )
        else:
            final_filename = f"unknown_{timestamp}{ext}"
            final_path = os.path.join(app.config["UPLOAD_FOLDER"], final_filename)
            image.save(final_path)
            c.execute(
                "INSERT INTO attendance (employee_id, image_path) VALUES (?, ?)",
                (None, final_path),
            )
            conn.commit()
            conn.close()
            return jsonify({"status": "fail", "message": "No match found"})
    return jsonify({"status": "fail", "message": "No image uploaded"})


@app.route("/register_employee", methods=["POST"])
def register_employee():
    nickname = request.form.get("nickname")
    image = request.files.get("image")
    if nickname and image:
        ext = os.path.splitext(image.filename)[1] or ".jpg"
        conn = get_db()
        c = conn.cursor()
        c.execute(
            "INSERT INTO employees (nickname, image_path) VALUES (?, ?)",
            (nickname, ""),
        )
        emp_id = c.lastrowid
        filename = f"{emp_id}{ext}"
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image.save(image_path)
        c.execute(
            "UPDATE employees SET image_path = ? WHERE id = ?",
            (image_path, emp_id),
        )
        conn.commit()
        conn.close()
        return jsonify(
            {"status": "success", "employee_id": emp_id, "nickname": nickname}
        )
    return jsonify({"status": "fail", "message": "Missing data"})


@app.route("/result")
def result():
    # Accept query params for status, employee_id, nickname, message, loading
    status = request.args.get("status")
    employee_id = request.args.get("employee_id")
    nickname = request.args.get("nickname")
    message = request.args.get("message")
    loading = request.args.get("loading") == "true"

    attendance_entries = []
    emp_id = None
    if employee_id:
        emp_id = employee_id
    elif nickname:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT id FROM employees WHERE nickname = ?", (nickname,))
        row = c.fetchone()
        if row:
            emp_id = row["id"]
        conn.close()
    if emp_id:
        conn = get_db()
        c = conn.cursor()
        c.execute(
            "SELECT timestamp, image_path FROM attendance WHERE employee_id = ? ORDER BY timestamp DESC LIMIT 10",
            (emp_id,),
        )
        attendance_entries = c.fetchall()
        conn.close()

    return render_template(
        "result.html",
        status=status,
        employee_id=emp_id,
        nickname=nickname,
        message=message,
        loading=loading,
        attendance_entries=attendance_entries,
    )


# Serve uploaded images
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    init_db()
    # Watch templates and static folders for changes
    extra_files = []
    for folder in ["src/templates", "src/static"]:
        for root, dirs, files in os.walk(folder):
            for f in files:
                extra_files.append(os.path.join(root, f))
    app.run(debug=True, extra_files=extra_files)
