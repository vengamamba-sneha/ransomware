from flask import Flask, jsonify, render_template, request
import os
import yara
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging

app = Flask(_name_)

# Set up logging for apscheduler
logging.basicConfig(level=logging.DEBUG)
scheduler_logger = logging.getLogger('apscheduler')

# Load YARA rules
rules = yara.compile(filepath='C:/Tools/ransomware_scanner_project/ransomware_rules.yar')

# Global scan progress
scan_progress = {
    "progress": 0,
    "scanned_files": [],
    "detected_files": [],
    "scanning": False,
    "scheduled_alert": ""
}

# Scan files and update progress
def scan_files(directory):
    global scan_progress
    detected_files = []
    total_files = 0

    # Set scanning to true to indicate scan is in progress
    scan_progress["scanning"] = True

    for root, dirs, files in os.walk(directory):
        total_files += len(files)

    if total_files == 0:
        scan_progress["progress"] = 100
        scan_progress["scanning"] = False
        return

    scanned_files = 0
    batch_update = 100

    def process_file(file_path):
        try:
            matches = rules.match(file_path)
            if matches:
                detected_files.append(file_path)
        except Exception:
            pass

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            scan_progress["scanned_files"].append(file_path)

            process_file(file_path)
            scanned_files += 1

            if scanned_files % batch_update == 0 or scanned_files == total_files:
                scan_progress["progress"] = (scanned_files / total_files) * 100

    scan_progress["detected_files"] = detected_files
    scan_progress["scanning"] = False
    scan_progress["progress"] = 100

    # If this was a scheduled scan, set an alert message
    if scheduler.get_job('scheduled_scan'):
        if detected_files:
            scan_progress["scheduled_alert"] = f"Scheduled Scan Alert: Ransomware detected at {datetime.now().strftime('%H:%M:%S')}."
        else:
            scan_progress["scheduled_alert"] = f"Scheduled Scan: No ransomware detected at {datetime.now().strftime('%H:%M:%S')}."

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    global scan_progress
    directory_to_scan = "C:/Tools"

    scan_progress = {
        "progress": 0,
        "scanned_files": [],
        "detected_files": [],
        "scanning": True,
        "scheduled_alert": ""
    }

    thread = threading.Thread(target=scan_files, args=(directory_to_scan,))
    thread.start()

    return jsonify({"message": "Scan started!"})

@app.route('/progress', methods=['GET'])
def get_progress():
    return jsonify(scan_progress)

@app.route('/schedule_scan', methods=['POST'])
def schedule_scan():
    time_to_run = request.json.get("time")  # Format "HH:MM"
    hour, minute = map(int, time_to_run.split(":"))

    # Schedule the scan to run daily at the specified time
    try:
        scheduler.add_job(
            lambda: scan_files("C:/Tools"), 
            trigger='cron', 
            hour=hour, 
            minute=minute, 
            id='scheduled_scan', 
            replace_existing=True
        )
        return jsonify({"message": f"Scheduled scan set for {time_to_run} daily."})
    except Exception as e:
        return jsonify({"message": f"Failed to set schedule: {e}"}), 500

# Start scheduler with error handling for visibility
try:
    scheduler = BackgroundScheduler()
    scheduler.start()
    scheduler_logger.info("Scheduler started successfully.")
except Exception as e:
    scheduler_logger.error("Failed to start scheduler: %s", e)

if _name_ == '_main_':
    app.run(debug=True, port=5000)  # Adjust port if needed
