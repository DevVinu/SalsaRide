import asyncio
import pytest
from app.schemas.user import UserCreate, UserLogin
from app.schemas.traffic import LocationPing, SimulatedVehicleInject
from app.api.auth import register, login
from app.api.junctions import list_junctions, find_nearby_junctions, get_junction, create_junction
from app.schemas.junction import JunctionCreate
from app.api.traffic import ingest_location_ping, get_junction_traffic_status
from app.api.signals import get_virtual_signal_state, step_virtual_signal
from app.api.simulation import apply_simulation_preset, inject_simulated_vehicle, clear_simulation
from app.core.constants import Direction


async def _run_auth_endpoints():
    user_in = UserCreate(
        email="direct.test@smartflow.io",
        password="SecurePassword123!",
        full_name="Direct Tester",
        role="DRIVER",
        location_sharing_enabled=True,
    )
    res_reg = await register(user_in)
    assert res_reg["access_token"] is not None
    assert res_reg["user"]["email"] == "direct.test@smartflow.io"

    login_in = UserLogin(
        email="direct.test@smartflow.io",
        password="SecurePassword123!",
    )
    res_login = await login(login_in)
    assert res_login["access_token"] is not None


def test_auth_endpoints():
    asyncio.run(_run_auth_endpoints())


async def _run_junction_endpoints():
    # Ensure test junction
    defaults = [
        JunctionCreate(
            junction_code="NYC_GCT_42",
            name="Grand Central & 42nd St Crossing",
            city="New York",
            address="Park Ave & E 42nd St, New York, NY",
            latitude=40.7516,
            longitude=-73.9767,
            detection_radius_meters=500,
            inner_zone_meters=150,
            mid_zone_meters=300,
        ),
    ]
    for d in defaults:
        await create_junction(d)

    junctions = await list_junctions()
    assert len(junctions) >= 1
    first_junc = junctions[0]
    j_name = first_junc.get("name") if isinstance(first_junc, dict) else first_junc.name
    j_id = first_junc.get("id") if isinstance(first_junc, dict) else first_junc.id
    assert j_name is not None

    # Test nearby search around Grand Central NYC (40.7516, -73.9767)
    nearby = await find_nearby_junctions(latitude=40.7516, longitude=-73.9767, max_radius_meters=1000.0)
    assert len(nearby) > 0
    assert nearby[0]["distance_to_user_meters"] < 50.0

    # Get specific junction
    fetched = await get_junction(j_id)
    fetched_id = fetched.get("id") if isinstance(fetched, dict) else fetched.id
    assert fetched_id == j_id


def test_junction_endpoints():
    asyncio.run(_run_junction_endpoints())


async def _run_traffic_ping():
    # 1. In-zone ping (North of Grand Central)
    ping_in = LocationPing(
        user_id="COMMUTER-DIR-01",
        latitude=40.7536,
        longitude=-73.9767,
        speed_kmh=18.0,
        is_emergency=False,
    )
    res_in = await ingest_location_ping(ping_in)
    assert res_in["status"] == "IN_ZONE"
    assert res_in["observation"]["corridor"] == Direction.NORTH
    assert "advisory" in res_in and res_in["advisory"] is not None

    # 2. Out-of-zone ping (Los Angeles coordinates)
    ping_out = LocationPing(
        user_id="COMMUTER-FAR",
        latitude=34.0522,
        longitude=-118.2437,
        speed_kmh=60.0,
    )
    res_out = await ingest_location_ping(ping_out)
    assert res_out["status"] == "OUT_OF_ZONE"


def test_traffic_ping_and_corridor_assignment():
    asyncio.run(_run_traffic_ping())


async def _run_simulation_and_signal():
    junctions = await list_junctions()
    junc_id = junctions[0].get("id") if isinstance(junctions[0], dict) else junctions[0].id

    # Get virtual signal state
    sig_state = await get_virtual_signal_state(junc_id)
    assert sig_state.current_phase is not None
    assert sig_state.remaining_seconds >= 0

    # Apply morning rush preset
    preset_res = await apply_simulation_preset(junc_id, preset="morning_rush")
    assert preset_res["preset_applied"] == "morning_rush"
    assert preset_res["total_vehicles_injected"] > 0

    # Check traffic status after simulation
    status_res = await get_junction_traffic_status(junc_id)
    assert status_res.total_participating_vehicles > 0
    assert status_res.corridors["NORTH"].vehicle_count > 0

    # Step phase
    step_res = await step_virtual_signal(junc_id)
    assert step_res["status"] == "SUCCESS"

    # Clear simulation
    clear_res = await clear_simulation(junc_id)
    assert clear_res["status"] == "SUCCESS"

    # Verify cleared
    post_clear = await get_junction_traffic_status(junc_id)
    assert post_clear.total_participating_vehicles == 0


def test_virtual_signal_and_simulation():
    asyncio.run(_run_simulation_and_signal())
