import os
import json
import requests
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# =========================
# ENV VARIABLES (ONLY TOKENS)
# =========================

AUTHORIZATION = os.getenv("AUTHORIZATION", "")
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")

DEVICE_ID = os.getenv("DEVICE_ID", "")
NEW_DEVICE_ID = os.getenv("NEW_DEVICE_ID", "")

APP_NAME = os.getenv("APP_NAME", "")
PACKAGE_NAME = os.getenv("PACKAGE_NAME", "")
PLATFORM = os.getenv("PLATFORM", "")
DEVICE_OS = os.getenv("DEVICE_OS", "")

USER_AGENT = os.getenv("USER_AGENT", "")
ORIGIN = os.getenv("ORIGIN", "")

PROFILE_URL = os.getenv("PROFILE_URL", "")

# =========================
# FIXED API URL (HARD CODED)
# =========================

CHALLAN_API_URL = "https://challan.parkplus.io/api/v1/challan/challan-list"


class handler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):

        try:
            query = parse_qs(urlparse(self.path).query)

            vehicle_number = query.get("vehicle", [""])[0]
            page = query.get("page", ["1"])[0]
            limit = query.get("limit", ["50"])[0]
            status_filter = query.get("status", ["PENDING"])[0]

            if not vehicle_number:
                return self.send_json(
                    {"error": "vehicle parameter required"},
                    400
                )

            headers = {
                "accept": "application/json",
                "authorization": AUTHORIZATION,
                "client-id": CLIENT_ID,
                "client-secret": CLIENT_SECRET,
                "device-id": DEVICE_ID,
                "new-device-id": NEW_DEVICE_ID,
                "app-name": APP_NAME,
                "package-name": PACKAGE_NAME,
                "platform": PLATFORM,
                "device-os": DEVICE_OS,
                "origin": ORIGIN,
                "user-agent": USER_AGENT
            }

            # =========================
            # CHALLAN API CALL
            # =========================

            challan_response = requests.get(
                CHALLAN_API_URL,
                headers=headers,
                params={
                    "vehicle_number": vehicle_number,
                    "status": status_filter,
                    "page": page,
                    "limit": limit
                },
                timeout=30
            )

            try:
                challan_data = challan_response.json()
            except:
                challan_data = {
                    "raw_response": challan_response.text
                }

            # =========================
            # PROFILE API CALL
            # =========================

            profile_data = None

            if PROFILE_URL:

                try:
                    profile_response = requests.get(
                        PROFILE_URL,
                        headers=headers,
                        timeout=30
                    )

                    profile_data = profile_response.json()

                except Exception as profile_error:
                    profile_data = {
                        "error": str(profile_error)
                    }

            # =========================
            # FINAL RESPONSE
            # =========================

            return self.send_json({
                "success": True,
                "vehicle_number": vehicle_number,
                "challan": challan_data,
                "profile": profile_data
            })

        except Exception as e:

            return self.send_json({
                "success": False,
                "error": str(e)
            }, 500)
