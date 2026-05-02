import requests
from bs4 import BeautifulSoup
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # যাতে অন্য ওয়েবসাইট থেকেও কল করা যায়

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
    "Referer": "https://vahanx.in/",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br"
}

def get_comprehensive_vehicle_details(rc_number: str) -> dict:
    rc = rc_number.strip().upper()
    url = f"https://vahanx.in/rc-search/{rc}"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        return {"error": f"Failed to fetch data: {str(e)}"}

    def extract_card(label):
        for div in soup.select(".hrcd-cardbody"):
            span = div.find("span")
            if span and label.lower() in span.text.lower():
                p = div.find("p")
                return p.get_text(strip=True) if p else None
        return None

    def extract_from_section(header_text, keys):
        section = soup.find("h3", string=lambda s: s and header_text.lower() in s.lower())
        section_card = section.find_parent("div", class_="hrc-details-card") if section else None
        result = {}
        for key in keys:
            span = section_card.find("span", string=lambda s: s and key in s) if section_card else None
            if span:
                val = span.find_next("p")
                result[key.lower().replace(" ", "_")] = val.get_text(strip=True) if val else None
        return result

    def get_value(label):
        try:
            div = soup.find("span", string=label)
            if div:
                div = div.find_parent("div")
                p = div.find("p") if div else None
                return p.get_text(strip=True) if p else None
        except:
            return None

    try:
        registration_number = soup.find("h1").text.strip()
    except:
        registration_number = rc

    modal_name = extract_card("Modal Name") or get_value("Model Name")
    owner_name = extract_card("Owner Name") or get_value("Owner Name")
    code = extract_card("Code")
    city = extract_card("City Name") or get_value("City Name")
    phone = extract_card("Phone") or get_value("Phone")
    website = extract_card("Website")
    address = extract_card("Address") or get_value("Address")

    ownership = extract_from_section("Ownership Details", ["Owner Name", "Father's Name", "Owner Serial No", "Registration Number", "Registered RTO"])
    vehicle = extract_from_section("Vehicle Details", ["Model Name", "Maker Model", "Vehicle Class", "Fuel Type", "Fuel Norms", "Cubic Capacity", "Seating Capacity"])

    insurance_expired_box = soup.select_one(".insurance-alert-box.expired .title")
    expired_days = None
    if insurance_expired_box:
        match = re.search(r"(\d+)", insurance_expired_box.text)
        expired_days = int(match.group(1)) if match else None
    
    insurance = extract_from_section("Insurance Information", ["Insurance Company", "Insurance No", "Insurance Expiry", "Insurance Upto"])
    insurance_status = "Expired" if expired_days else "Active"
    
    validity = extract_from_section("Important Dates", ["Registration Date", "Vehicle Age", "Fitness Upto", "Insurance Upto", "Insurance Expiry In", "Tax Upto", "Tax Paid Upto"])
    puc = extract_from_section("PUC Details", ["PUC No", "PUC Upto"])
    other = extract_from_section("Other Information", ["Financer Name", "Financier Name", "Cubic Capacity", "Seating Capacity", "Permit Type", "Blacklist Status", "NOC Details"])

    data = {
        "registration_number": registration_number,
        "status": "success",
        "basic_info": {"model_name": modal_name, "owner_name": owner_name, "fathers_name": get_value("Father's Name") or ownership.get("father's_name"), "code": code, "city": city, "phone": phone, "website": website, "address": address},
        "ownership_details": {"owner_name": ownership.get("owner_name") or owner_name, "fathers_name": ownership.get("father's_name"), "serial_no": ownership.get("owner_serial_no") or get_value("Owner Serial No"), "rto": ownership.get("registered_rto") or get_value("Registered RTO")},
        "vehicle_details": {"maker": vehicle.get("model_name") or modal_name, "model": vehicle.get("maker_model") or get_value("Maker Model"), "vehicle_class": vehicle.get("vehicle_class") or get_value("Vehicle Class"), "fuel_type": vehicle.get("fuel_type") or get_value("Fuel Type"), "fuel_norms": vehicle.get("fuel_norms") or get_value("Fuel Norms"), "cubic_capacity": vehicle.get("cubic_capacity") or other.get("cubic_capacity"), "seating_capacity": vehicle.get("seating_capacity") or other.get("seating_capacity")},
        "insurance": {"status": insurance_status, "company": insurance.get("insurance_company") or get_value("Insurance Company"), "policy_number": insurance.get("insurance_no") or get_value("Insurance No"), "expiry_date": insurance.get("insurance_expiry") or get_value("Insurance Expiry"), "valid_upto": insurance.get("insurance_upto") or get_value("Insurance Upto"), "expired_days_ago": expired_days},
        "validity": {"registration_date": validity.get("registration_date") or get_value("Registration Date"), "vehicle_age": validity.get("vehicle_age") or get_value("Vehicle Age"), "fitness_upto": validity.get("fitness_upto") or get_value("Fitness Upto"), "insurance_upto": validity.get("insurance_upto") or get_value("Insurance Upto"), "tax_upto": validity.get("tax_upto") or validity.get("tax_paid_upto") or get_value("Tax Upto")},
        "puc_details": {"puc_number": puc.get("puc_no") or get_value("PUC No"), "puc_valid_upto": puc.get("puc_upto") or get_value("PUC Upto")},
        "other_info": {"financer": other.get("financer_name") or other.get("financier_name") or get_value("Financier Name"), "permit_type": other.get("permit_type") or get_value("Permit Type"), "blacklist_status": other.get("blacklist_status") or get_value("Blacklist Status"), "noc": other.get("noc_details") or get_value("NOC Details")}
    }

    def clean_dict(d):
        if isinstance(d, dict):
            return {k: clean_dict(v) for k, v in d.items() if v is not None and v != ""}
        return d
    
    return clean_dict(data)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "active", "endpoint": "/api/vahan?vahan_number=YOUR_RC"})

@app.route("/api/vahan", methods=["GET"])
def vahan_api():
    vahan_number = request.args.get("vahan_number")
    if not vahan_number:
        return jsonify({"error": "Please provide vahan_number parameter"}), 400
    
    result = get_comprehensive_vehicle_details(vahan_number)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)