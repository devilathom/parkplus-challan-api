
import os
import re
import requests

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

app = FastAPI(title="ParkPlus Challan API")


CHALLAN_API_URL = (
    "https://challan.parkplus.io/api/v1/challan/challan-list"
)


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


@app.get("/")
def home():
    return {
        "success": True,
        "message": "ParkPlus Challan API is running",
        "endpoint": "/fetch?vehicle=HR26EV0001"
    }


@app.get("/fetch")
def fetch_challan(
    vehicle: str = Query(...),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    status: str = Query("PENDING")
):
    vehicle = vehicle.upper().replace(" ", "")

    if not re.fullmatch(r"[A-Z0-9]{6,12}", vehicle):
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "Invalid vehicle number"
            }
        )

    headers = build_headers()

    if not headers["authorization"] or not headers["client-id"]:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Missing ParkPlus API credentials"
            }
        )

    try:
        challan_res = requests.get(
            CHALLAN_API_URL,
            headers=headers,
            params={
                "vehicle_number": vehicle,
                "status": status,
                "page": page,
                "limit": limit
            },
            timeout=25
        )

        try:
            challan_data = challan_res.json()
        except ValueError:
            challan_data = {
                "raw": challan_res.text[:3000]
            }

        if not challan_res.ok:
            return JSONResponse(
                status_code=502,
                content={
                    "success": False,
                    "error": "ParkPlus upstream API failed",
                    "upstream_status": challan_res.status_code,
                    "details": challan_data
                }
            )

        return {
            "success": True,
            "vehicle": vehicle,
            "challan": challan_data
        }

    except requests.Timeout:
        return JSONResponse(
            status_code=504,
            content={
                "success": False,
                "error": "ParkPlus API request timed out"
            }
        )

    except requests.RequestException as e:
        return JSONResponse(
            status_code=502,
            content={
                "success": False,
                "error": "ParkPlus connection failed",
                "details": str(e)
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )
