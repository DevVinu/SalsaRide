"""
SmartFlow Example: Real GPS Streamer Client
Demonstrates how to send real or simulated live GPS telemetry to the SmartFlow Traffic Management API.
Works with any device, OBD-II tracker, smartphone, or external GPS gateway.
"""

import requests
import time
import math

SMARTFLOW_API_URL = "http://127.0.0.1:8000/api/v1/traffic/ping"

# Example Junction: Grand Central NYC (40.7516, -73.9767)
TARGET_JUNCTION_LAT = 40.7516
TARGET_JUNCTION_LON = -73.9767

def send_gps_telemetry(user_id: str, latitude: float, longitude: float, speed_kmh: float = 30.0, is_emergency: bool = False):
    payload = {
        "user_id": user_id,
        "latitude": latitude,
        "longitude": longitude,
        "speed_kmh": speed_kmh,
        "is_emergency": is_emergency,
        "accuracy_meters": 3.0
    }
    
    try:
        response = requests.post(SMARTFLOW_API_URL, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "IN_ZONE":
                obs = data["observation"]
                adv = data["advisory"]
                print(f"[{user_id}] -> IN ZONE: {data['junction_name']}")
                print(f"       Corridor: {obs['corridor']} | Dist: {obs['distance_meters']:.1f}m | Zone: {obs['zone']}")
                print(f"       Signal: {adv['lamp']} | Rec. Speed: {adv['recommended_speed_kmh']} km/h")
            else:
                print(f"[{user_id}] -> OUT OF ZONE ({data.get('distance_to_nearest', 'N/A')}m to nearest junction)")
        else:
            print(f"API Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Failed to connect to SmartFlow API at {SMARTFLOW_API_URL}: {e}")

if __name__ == "__main__":
    print(f"Starting GPS Streamer -> Pinging {SMARTFLOW_API_URL}...\n")
    
    # Simulate a vehicle driving south down Park Ave towards Grand Central Crossing
    # Starting 450 meters North of the junction:
    start_offset_deg = 0.0040  # ~440 meters North
    
    for step in range(8):
        current_lat = TARGET_JUNCTION_LAT + (start_offset_deg * (1 - (step * 0.12)))
        current_lon = TARGET_JUNCTION_LON
        speed = 35.0 - (step * 3.0)  # slowing down as approaching
        
        send_gps_telemetry(
            user_id="REAL-GPS-USER-01",
            latitude=current_lat,
            longitude=current_lon,
            speed_kmh=speed,
            is_emergency=False
        )
        time.sleep(1.5)

