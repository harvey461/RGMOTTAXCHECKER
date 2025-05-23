from flask import Flask, request, render_template_string
import requests
import time
from datetime import datetime
import os

app = Flask(__name__)

# Set your DVLA API key as an environment variable on the host platform
API_KEY = os.getenv("DVLA_API_KEY")
URL = "https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles"
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

number_plates = [
    "1TRR", "LX58VOA", "RS06XXX", "RU68ERT", "WD63TZY", "WU66NUE", "WM19GYD", "BF16YCZ",
    "LD63RFE", "LC18WDE", "MF60OVG", "WJ20OPX", "WH21LSF", "WG69XUN", "WD69LTN", "WD22FEF",
    "VA17KNC", "WO23FAA", "WR23GUX", "WR23GUH", "LX17GUF", "WP66TCV", "WF68YRO", "WB19JJY"
]

def format_date(date_str):
    if not date_str or date_str == "N/A":
        return "N/A"
    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")

def check_vehicle(registration):
    response = requests.post(URL, headers=HEADERS, json={"registrationNumber": registration})
    if response.status_code == 200:
        data = response.json()
        return {
            "registration": registration,
            "make": data.get("make"),
            "model": data.get("model"),
            "tax_status": data.get("taxStatus"),
            "tax_due_date": format_date(data.get("taxDueDate", "N/A")),
            "mot_status": data.get("motStatus"),
            "mot_expiry_date": format_date(data.get("motExpiryDate", "N/A"))
        }
    else:
        return {
            "registration": registration,
            "error": f"HTTP {response.status_code} - {response.text}"
        }

def pretty_vehicle_output(data):
    if "error" in data:
        return f"<strong>{data['registration']}</strong><br>Error: {data['error']}<br><br>"
    make = data.get("make", "Unknown").capitalize()
    model = data.get("model") or "(Not listed)"
    tax_status = data.get("tax_status", "Unknown")
    tax_due = data.get("tax_due_date", "Unknown")
    mot_status = data.get("mot_status", "Unknown")
    mot_due = data.get("mot_expiry_date", "Unknown")

    return f"""
        <strong>{data['registration']}</strong><br>
        Make: {make}<br>
        Model: {model}<br>
        Tax status: {tax_status} until {tax_due}<br>
        MOT status: MOT {mot_status.lower()} until {mot_due}<br><br>
    """

@app.route("/", methods=["GET", "POST"])
def home():
    output = ""
    if request.method == "POST":
        plate = request.form.get("plate", "").strip().upper()
        if plate == "ALL":
            for p in number_plates:
                data = check_vehicle(p)
                output += pretty_vehicle_output(data)
                time.sleep(1)
        else:
            data = check_vehicle(plate)
            output = pretty_vehicle_output(data)
    return render_template_string("""
        <h1>🚗 Vehicle Tax & MOT Checker</h1>
        <form method="post">
            <input name="plate" placeholder="Enter number plate or 'ALL'">
            <button type="submit">Check</button>
        </form>
        <hr>
        <div style="font-family: monospace;">{{ output|safe }}</div>
    """, output=output)

if __name__ == "__main__":
    app.run(debug=True)
