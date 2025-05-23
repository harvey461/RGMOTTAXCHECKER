import requests
import time
import csv
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
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

def pretty_print_vehicle(data):
    registration = data.get("registration", "Unknown")
    make = data.get("make")
    make = make.capitalize() if make else "Unknown"

    model = data.get("model")
    model = model.capitalize() if model else "(Not listed)"

    tax_status = data.get("tax_status", "Unknown")
    tax_due = data.get("tax_due_date", "Unknown")
    mot_status = data.get("mot_status", "Unknown")
    mot_due = data.get("mot_expiry_date", "Unknown")

    print(f"\n{registration}")
    print(f"Make: {make}")
    print(f"Model: {model}")
    print(f"Tax status: {tax_status} until {tax_due}")
    print(f"MOT status: MOT {mot_status.lower()} until {mot_due}")

def main():
    while True:
        print("\n📋 Registered vehicles:")
        for i, plate in enumerate(number_plates, 1):
            print(f"{i}. {plate}")
        print("\nType a number plate to check just one, 'all' to check them all, or 'exit' to quit:")

        choice = input("Your choice: ").strip().upper()

        if choice == "EXIT":
            print("👋 Goodbye!")
            break
        elif choice == "ALL":
            selected_plates = number_plates
        elif choice in number_plates:
            selected_plates = [choice]
        else:
            print("❌ Invalid input. Try again.")
            continue

        results = []
        print("\n🔍 Checking vehicle(s)...\n")
        for plate in selected_plates:
            result = check_vehicle(plate)
            results.append(result)
            time.sleep(1)  # avoid hammering the API

        for vehicle in results:
            if "error" not in vehicle:
                pretty_print_vehicle(vehicle)
            else:
                print(f"\n{vehicle['registration']}")
                print(f"❌ Error: {vehicle['error']}")

        if results:
            with open("dvla_check_results.csv", "w", newline="") as f:
                fieldnames = ["registration", "make", "model", "tax_status", "tax_due_date", "mot_status", "mot_expiry_date"]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                valid_results = [r for r in results if 'error' not in r]
                writer.writerows(valid_results)

            print("\n✅ Done. Results saved to 'dvla_check_results.csv'.")
            time.sleep(8)
if __name__ == "__main__":
    main()
