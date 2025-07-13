# Use official Python image
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

# Create data directory for uploads and database
RUN mkdir -p /data/uploads

ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV UPLOAD_FOLDER=/data/uploads
ENV DATABASE=/data/attendance.db

EXPOSE 8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
