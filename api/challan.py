import os
import time
import json
import requests
from fastapi import FastAPI, Query

app = FastAPI()

# =========================
# ENV VARIABLES
# =========================

AUTHORIZATION = os.getenv("AUTHORIZATION", "")
CLIENT_ID = os.getenv("CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")

DEVICE_ID = os.getenv("DEVICE_ID", "")
NEW_DEVICE_ID = os.getenv("NEW_DEVICE_ID", "")

APP_NAME = os.getenv("APP_NAME", "Park+ PWA")
PACKAGE_NAME = os.getenv("PACKAGE_NAME", "web.pwa")
PLATFORM = os.getenv("PLATFORM", "web")
DEVICE_OS = os.getenv("DEVICE_OS", "unknown")

USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0")
ORIGIN = os.getenv("ORIGIN", "https://parkplus.io")

PROFILE_URL = os.getenv("PROFILE_URL", "https://user-service.parkplus.io/api/user/profile/")

CHALLAN_API_URL = "https://challan.parkplus.io/api/v1/challan/challan-list"


# =========================
# SIMPLE TOKEN CACHE
# =========================

_token_cache = {
    "token": AUTHORIZATION,
    "time": time.time()
}


def get_token():
    return _token_cache["token"]


# =========================
# HEADERS BUILDER
# =========================

def build_headers():
    return {
        "accept": "application/json",
        "authorization": get_token(),
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
# API ROUTE
# =========================

@app.get("/api/challan")
def get_challan(
    vehicle: str = Query(...),
    page: int = 1,
    limit: int = 50,
    status: str = "PENDING"
):

    headers = build_headers()

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

    return {
        "success": True,
        "vehicle": vehicle,
        "challan": challan_data,
        "profile": profile_data
    }


# =========================
# ✅ VERCEL FIX (IMPORTANT)
# =========================

from mangum import Mangum

handler = Mangum(app)
