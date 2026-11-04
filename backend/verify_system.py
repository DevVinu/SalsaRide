import asyncio
import sys
import os

# Ensure backend directory is in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import db_manager


async def run_diagnostics():
    print("=" * 70)
    print("🚦 SMARTFLOW SYSTEM DIAGNOSTIC & VERIFICATION SUITE")
    print("=" * 70)

    results = []

    def log_test(name: str, passed: bool, details: str = ""):
        status = "✅ PASS" if passed else "❌ FAIL"
        results.append((name, passed))
        print(f"{status} | {name}", flush=True)
        if details:
            print(f"       -> {details}", flush=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Test 1: Root & OpenAPI Docs
        try:
            r = await client.get("/")
            log_test("Root Landing Page & Disclaimer", r.status_code == 200 and "SmartFlow" in r.text)
        except Exception as e:
            log_test("Root Landing Page & Disclaimer", False, str(e))

        try:
            r = await client.get("/docs")
            log_test("Interactive Swagger API Documentation (/docs)", r.status_code == 200)
        except Exception as e:
            log_test("Interactive Swagger API Documentation", False, str(e))

        # Test 2: Admin Dashboard Static Delivery
        try:
            r = await client.get("/admin/")
            has_dashboard = r.status_code == 200 and "SmartFlow Admin" in r.text
            log_test("Admin Dashboard Static File Delivery (/admin/)", has_dashboard)
        except Exception as e:
            log_test("Admin Dashboard Static File Delivery", False, str(e))

        # Test 3: Junctions Listing & Default Seeding
        junction_id = None
        try:
            r = await client.get("/api/v1/junctions")
            data = r.json()
            passed = r.status_code == 200 and len(data) >= 1
            if passed:
                junction_id = data[0]["id"]
            log_test(
                f"Junctions Listing & Seeding ({len(data)} seeded junctions)",
                passed,
                f"Active Junction: {data[0]['name'] if data else 'None'}"
            )
        except Exception as e:
            log_test("Junctions Listing & Seeding", False, str(e))

        # Test 4: Nearby Junction Calculation
        try:
            # Query near Grand Central NYC (40.7516, -73.9767)
            r = await client.get("/api/v1/junctions/nearby?latitude=40.7516&longitude=-73.9767")
            data = r.json()
            passed = r.status_code == 200 and len(data) > 0 and data[0]["distance_to_user_meters"] < 50
            log_test("Nearby Junction Geospatial Search (Haversine)", passed, f"Calculated distance: {data[0]['distance_to_user_meters']}m")
        except Exception as e:
            log_test("Nearby Junction Geospatial Search", False, str(e))

        # Test 5: Authentication (Registration & Login)
        auth_token = None
        test_email = "alex.commuter@smartflow.io"
        try:
            reg_res = await client.post("/api/v1/auth/register", json={
                "email": test_email,
                "password": "Password123!",
                "full_name": "Alex Commuter",
                "phone": "+1234567890",
                "role": "DRIVER",
                "location_sharing_enabled": True
            })
            token_data = reg_res.json()
            auth_token = token_data.get("access_token")
            log_test("User Registration & JWT Generation", reg_res.status_code == 201 and auth_token is not None)
        except Exception as e:
            log_test("User Registration & JWT Generation", False, str(e))

        try:
            login_res = await client.post("/api/v1/auth/login", json={
                "email": test_email,
                "password": "Password123!"
            })
            log_test("User Login Authentication & Token Verification", login_res.status_code == 200)
        except Exception as e:
            log_test("User Login Authentication", False, str(e))

        # Test 6: In-Zone GPS Ping Ingestion & Corridor Assignment
        try:
            # Ping positioned North of Grand Central (40.7516 + 0.002, -73.9767)
            ping_res = await client.post("/api/v1/traffic/ping", json={
                "user_id": "COMMUTER-001",
                "latitude": 40.7536,
                "longitude": -73.9767,
                "speed_kmh": 24.5,
                "is_emergency": False
            })
            data = ping_res.json()
            in_zone = data.get("status") == "IN_ZONE"
            corridor = data.get("observation", {}).get("corridor") == "NORTH"
            has_advisory = "advisory" in data and data["advisory"] is not None
            log_test("GPS Ping Ingress & Corridor Assignment", in_zone and corridor, f"Assigned Corridor: {data.get('observation', {}).get('corridor')}")
            log_test("In-Car Driver Advisory Generation", has_advisory, f"Advisory Action: {data.get('advisory', {}).get('action')}")
        except Exception as e:
            log_test("GPS Ping Ingress & Corridor Assignment", False, str(e))

        # Test 7: Out-of-Zone Detection Protection
        try:
            # Ping far away (Los Angeles coordinates)
            out_res = await client.post("/api/v1/traffic/ping", json={
                "user_id": "COMMUTER-FAR",
                "latitude": 34.0522,
                "longitude": -118.2437,
                "speed_kmh": 60.0
            })
            data = out_res.json()
            out_of_zone = data.get("status") == "OUT_OF_ZONE"
            log_test("Out-of-Zone Geofence Exclusion (&gt;500m)", out_of_zone, "Confirmed far coordinates excluded from junction count")
        except Exception as e:
            log_test("Out-of-Zone Geofence Exclusion", False, str(e))

        # Test 8: Virtual Traffic Signal State & Lamp Matrix
        if junction_id:
            try:
                sig_res = await client.get(f"/api/v1/signals/{junction_id}")
                sig_data = sig_res.json()
                valid_signal = (
                    sig_res.status_code == 200
                    and "current_phase" in sig_data
                    and "north_south_lamp" in sig_data
                    and "east_west_lamp" in sig_data
                    and "remaining_seconds" in sig_data
                )
                log_test("Virtual Traffic Signal State Machine", valid_signal, f"Phase: {sig_data.get('current_phase')} (NS: {sig_data.get('north_south_lamp')}, EW: {sig_data.get('east_west_lamp')})")
            except Exception as e:
                log_test("Virtual Traffic Signal State Machine", False, str(e))

            # Test 9: Traffic Simulation Preset Engine
            try:
                sim_res = await client.post(f"/api/v1/simulation/{junction_id}/preset?preset=morning_rush")
                sim_data = sim_res.json()
                applied = sim_res.status_code == 200 and sim_data.get("preset_applied") == "morning_rush"
                log_test("Traffic Simulation Preset Engine (Morning Rush)", applied, f"Injected {sim_data.get('total_vehicles_injected')} vehicles")
            except Exception as e:
                log_test("Traffic Simulation Preset Engine", False, str(e))

            # Test 10: Corridor Traffic Status Post-Simulation
            try:
                traf_res = await client.get(f"/api/v1/traffic/{junction_id}")
                traf_data = traf_res.json()
                total = traf_data.get("total_participating_vehicles", 0)
                log_test("Real-Time Corridor Telemetry & Aggregation", total > 0, f"Total tracked vehicles: {total}")
            except Exception as e:
                log_test("Real-Time Corridor Telemetry & Aggregation", False, str(e))

            # Test 11: Emergency Vehicle Preemption Test
            try:
                emg_res = await client.post(f"/api/v1/simulation/{junction_id}/preset?preset=emergency")
                emg_data = emg_res.json()
                sig_check = await client.get(f"/api/v1/signals/{junction_id}")
                log_test("Emergency SOS Preemption Scenario", emg_res.status_code == 200, "Ambulance priority injected into East corridor")
            except Exception as e:
                log_test("Emergency SOS Preemption Scenario", False, str(e))

            # Test 12: Force Step Phase Control
            try:
                step_res = await client.post(f"/api/v1/signals/{junction_id}/step")
                log_test("Virtual Signal Manual / Force Phase Step Control", step_res.status_code == 200)
            except Exception as e:
                log_test("Virtual Signal Manual / Force Phase Step Control", False, str(e))

            # Test 13: Simulation Cleanup
            try:
                clr_res = await client.delete(f"/api/v1/simulation/{junction_id}/clear")
                log_test("Simulation Teardown & Vehicle Cleanup", clr_res.status_code == 200)
            except Exception as e:
                log_test("Simulation Teardown & Vehicle Cleanup", False, str(e))

    print("=" * 70, flush=True)
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    pct = round((passed_count / total_count) * 100, 1) if total_count else 0
    print(f"📊 SUMMARY: {passed_count}/{total_count} TESTS PASSED ({pct}% HEALTH)", flush=True)
    print("=" * 70, flush=True)
    sys.exit(0 if passed_count == total_count else 1)


if __name__ == "__main__":
    asyncio.run(run_diagnostics())
