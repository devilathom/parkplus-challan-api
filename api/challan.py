import os
import requests
from mangum import Mangum
from fastapi import FastAPI, Query

app = FastAPI()

CHALLAN_API_URL = "https://challan.parkplus.io/api/v1/challan/challan-list"


def headers():
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
        "user-agent": os.getenv("USER_AGENT", "Mozilla/5.0"),
    }


@app.get("/")
def get_challan(vehicle: str, page: int = 1, limit: int = 50, status: str = "PENDING"):

    res = requests.get(
        CHALLAN_API_URL,
        headers=headers(),
        params={
            "vehicle_number": vehicle,
            "status": status,
            "page": page,
            "limit": limit
        },
        timeout=30
    )

    try:
        return res.json()
    except:
        return {"error": res.text}


# IMPORTANT: Vercel entrypoint
handler = Mangum(app)
