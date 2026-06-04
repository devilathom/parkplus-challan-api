import os
import json
import requests
from urllib.parse import parse_qs


CHALLAN_API_URL = "https://challan.parkplus.io/api/v1/challan/challan-list"
PROFILE_URL = "https://user-service.parkplus.io/api/user/profile/"


def build_headers():
    return {
        "accept": "application/json",
        "authorization": os.getenv("AUTHORIZATION", ""),
        "client-id": os.getenv("CLIENT_ID", ""),
        "client-secret": os.getenv("CLIENT_SECRET", ""),
        "device-id": os.getenv("DEVICE_ID", ""),
        "new-device-id": os.getenv("NEW_DEVICE_ID", ""),
        "app-name": os.getenv("APP_NAME", "Park+ PWA"),
        "package-name": os.getenv("PACKAGE_NAME", "web.pwa"),
        "platform": os.getenv("PLATFORM", "web"),
        "device-os": os.getenv("DEVICE_OS", "unknown"),
        "origin": os.getenv("ORIGIN", "https://parkplus.io"),
        "user-agent": os.getenv("USER_AGENT", "Mozilla/5.0")
    }


def handler(request):
    try:

        # ✅ SAFE VERCEL QUERY PARSING
        query_string = getattr(request, "query_string", "")

        params = parse_qs(query_string)

        vehicle = params.get("vehicle", [None])[0]
        page = params.get("page", ["1"])[0]
        limit = params.get("limit", ["50"])[0]
        status = params.get("status", ["PENDING"])[0]

        if not vehicle:
            return response(400, {"error": "vehicle required"})

        headers = build_headers()

        # ---------------- CHALLAN API ----------------
        challan_res = requests.get(
            CHALLAN_API_URL,
            headers=headers,
            params={
                "vehicle_number": vehicle,
                "status": status,
                "page": page,
                "limit": limit
            },
            timeout=30
        )

        try:
            challan_data = challan_res.json()
        except:
            challan_data = {"raw": challan_res.text}

        # ---------------- PROFILE API ----------------
        profile_data = None
        try:
            profile_res = requests.get(
                PROFILE_URL,
                headers=headers,
                timeout=30
            )
            profile_data = profile_res.json()
        except Exception as e:
            profile_data = {"error": str(e)}

        return response(200, {
            "success": True,
            "vehicle": vehicle,
            "challan": challan_data,
            "profile": profile_data
        })

    except Exception as e:
        return response(500, {
            "success": False,
            "error": str(e)
        })


def response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(body)
    }


# Vercel entrypoint
app = handler
