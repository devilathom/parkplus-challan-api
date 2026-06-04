from http.server import BaseHTTPRequestHandler
import json
import requests
import os

PARKPLUS_TOKEN = os.getenv("PARKPLUS_TOKEN")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            from urllib.parse import urlparse, parse_qs

            query = parse_qs(urlparse(self.path).query)
            vehicle = query.get("vehicle", [""])[0]

            if not vehicle:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(
                    json.dumps({"error": "vehicle required"}).encode()
                )
                return

            headers = {
                "Authorization": PARKPLUS_TOKEN,
                "Accept": "application/json"
            }

            url = (
                "https://challan.parkplus.io/api/v1/challan/challan-list"
                f"?vehicle_number={vehicle}"
                "&status=PENDING&page=1&limit=50"
            )

            r = requests.get(url, headers=headers, timeout=30)

            self.send_response(r.status_code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(r.content)

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(
                json.dumps({"error": str(e)}).encode()
            )
