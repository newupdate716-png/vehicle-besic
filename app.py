from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ---------------- ROOT USAGE ----------------
@app.route("/", methods=["GET"])
def usage():
    return jsonify({
        "api": "Vehicle Info API",
        "method": "GET",
        "endpoint": "/info",
        "usage": "/info?vehicle=DL10CA7539",
        "description": "Fetch vehicle details using registration number",
        "status": "online"
    })


# ---------------- FAVICON FIX ----------------
@app.route('/favicon.ico')
def favicon():
    return '', 204


# ---------------- MAIN API ----------------
@app.route("/info", methods=["GET"])
def vehicle_info():
    reg_no = request.args.get("vehicle")

    if not reg_no:
        return jsonify({
            "status": False,
            "error": "Missing vehicle parameter",
            "example": "/info?vehicle=DL10CA7539"
        }), 400

    reg_no = reg_no.strip().upper()

    url = (
        "https://www.acko.com/api/sdui/central/auto-asset/vas/asset-header"
        f"?registration_number={reg_no}&source=vas_rto&include_vehicle_search_response=true"
    )

    headers = {
        "user-agent": "Dart/3.8 (dart:io)",
        "app_version": "12.1.1",
        "accept-encoding": "gzip",
        "content-type": "application/json",
        "enable_app_cache_bust": "true",
        "app-d2c-refresh-token": "eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICIwZmVmYzE3Yi03OGUwLTRkZjUtOGI4OC1iZmVmNDlkMGRkZTgifQ.eyJpYXQiOjE3NjMyNzE4NTIsImp0aSI6ImIzYjJiYWZlLTIzOGUtNDgxZS1hZGRjLTk0M2RjMjU0MzJlZiIsImlzcyI6Imh0dHBzOi8vY2VudHJhbC1hdXRoLXByb2QuaW50ZXJuYWwubGl2ZS5hY2tvLmNvbS9yZWFsbXMvYWNrbyIsImF1ZCI6Imh0dHBzOi8vY2VudHJhbC1hdXRoLXByb2QuaW50ZXJuYWwubGl2ZS5hY2tvLmNvbS9yZWFsbXMvYWNrbyIsInN1YiI6IlRvSVdlcFZnb0JBZ210eFZ4YjZia1EiLCJ0eXAiOiJPZmZsaW5lIiwiYXpwIjoiYWNrb19hcHAiLCJzZXNzaW9uX3N0YXRlIjoiNmM3OWZhMDUtN2E2ZS00NTBmLTk0ZDItNzg2OTYzODM5ZGFiIiwic2NvcGUiOiJvZmZsaW5lX2FjY2VzcyIsInNpZCI6IjZjNzlmYTA1LTdhNmUtNDUwZi05NGQyLTc4Njk2MzgzOWRhYiJ9.UjIvJGATuV6ybX36XReOTmz-mo92oWZUJxetzcn6DOw",
        "app-d2c-tracker-id": "0b88de87-e59b-41c0-9662-a58b4e81e7a1",
        "platform": "android",
        "host": "www.acko.com",
        "build_number": "335",
        "x-platform": "android",
        "app-d2c-access-token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJFUHhtZUwzV0hDLTVsNTQ1VHNld2kwYTU3SFRlZy0ySXpmZk9zM0hOUEhNIn0.eyJleHAiOjE3NjM0NDQ2NTIsImlhdCI6MTc2MzI3MTg1MiwiYXV0aF90aW1lIjoxNzYzMjcxODUxLCJqdGkiOiIwNWE3YjM5Ny1lZmU1LTQxNWYtYTBkMi0xZjA5M2UwNWNkNTQiLCJpc3MiOiJodHRwczovL2NlbnRyYWwtYXV0aC1wcm9kLmludGVybmFsLmxpdmUuYWNrby5jb20vcmVhbG1zL2Fja28iLCJzdWIiOiJUb0lXZXBWZ29CQWdtdHhWeGI2YmtRIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiYWNrb19hcHAiLCJzZXNzaW9uX3N0YXRlIjoiNmM3OWZhMDUtN2E2ZS00NTBmLTk0ZDItNzg2OTYzODM5ZGFiIiwic2NvcGUiOiJvZmZsaW5lX2FjY2VzcyIsInNpZCI6IjZjNzlmYTA1LTdhNmUtNDUwZi05NGQyLTc4Njk2MzgzOWRhYiIsIm1pZ3JhdGlvbl9rZXlzIjp7InVzZXJfaWQiOiIxNTUxMDEwODcifX0.SPuK5B7YMgY69XMRPidzPOBtbWa8cIn_T2mqcnUXZFg1lBESXuDiFPPNLKDGx0sWz153UdOyUr70zZSjmwQ4yGQKniCMgtiIHIsl8AxZIYeM6FOQ8pDSRg7fktkmGWHYlkdqA2OiTRyp-oRHQMWRUyQ1zDu_7Hmg47Ix1Nrzsqh9DfGWypxv_6majPLZTKVXiwxIsFnBTTxF1nCVIUmCbxWjgSpQoVYJXrhqtklg9lVp5w551rfVyyL69dDfA3UBSk-RXsqedWqvfoUPV6anO5Aj9ovRnSMLTpZizihrOZX-eE-rhn3RW72zZ0CS6IjVs-WJ_g__iBTbmE6jWD_juA"
    }

    cookies = {
        "__cf_bm": "ELMt60q57EQLwo39Czom_Vk0_GnNnQNtlxih8.YRBSo-1760139914-1.0.1.1-iJPZLqWYwveXJugtsW0KRhb25F27ulbHLiNFNgF5eS8snRX4bz.MtvDsZx6WTU3oGjTHWaDWUuxFvDJgcB7wkQnsv8ongKfBYZChNJJWVqk",
        "_ga": "GA1.1.673981056.1759707626",
        "_gid": "GA1.1.1759707628.1759707628"
    }

    try:
        r = requests.get(url, headers=headers, cookies=cookies, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        return jsonify({
            "status": False,
            "error": str(e)
        }), 500

    # ---------- SAFE EXTRACTION ----------
    search_data = None

    if isinstance(data, dict):
        if isinstance(data.get("searchApiData"), dict):
            search_data = data["searchApiData"]
        elif isinstance(data.get("data"), dict) and isinstance(data["data"].get("searchApiData"), dict):
            search_data = data["data"]["searchApiData"]
        elif isinstance(data.get("pageProps"), dict) and isinstance(data["pageProps"].get("searchApiData"), dict):
            search_data = data["pageProps"]["searchApiData"]

    if not search_data:
        return jsonify({
            "status": False,
            "message": "No data found or invalid vehicle number"
        }), 404

    return jsonify(search_data)


# ---------------- RUN SERVER ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)