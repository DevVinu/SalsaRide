from fastapi import APIRouter, HTTPException, Query, status
from typing import Dict, Any, List
from datetime import datetime
from app.schemas.traffic import LocationPing, CorridorTrafficSummary, JunctionTrafficStatus
from app.services.traffic_service import traffic_service
from app.services.signal_controller import signal_manager
from app.services.geo_service import calculate_haversine_distance
from app.websockets.connection_manager import ws_manager
from app.api.junctions import list_junctions, get_junction

router = APIRouter(prefix="/traffic", tags=["Traffic Monitoring"])


@router.post("/ping")
async def ingest_location_ping(ping: LocationPing):
    """
    Core mobile telemetry ingress:
    1. Obtains user's latitude and longitude.
    2. Identifies if the user is approaching any registered junction.
    3. Calculates distance and approach corridor.
    4. Records anonymized participation.
    5. Advances signal controller and broadcasts live updates.
    """
    user_id = ping.user_id or "ANON_COMMUTER"
    junctions = await list_junctions()

    detected_junction = None
    min_dist = float("inf")

    for j in junctions:
        j_lat = j.latitude if hasattr(j, "latitude") else j["latitude"]
        j_lon = j.longitude if hasattr(j, "longitude") else j["longitude"]
        j_radius = j.detection_radius_meters if hasattr(j, "detection_radius_meters") else j.get("detection_radius_meters", 500)

        dist = calculate_haversine_distance(
            ping.latitude, ping.longitude, j_lat, j_lon
        )
        if dist <= j_radius and dist < min_dist:
            min_dist = dist
            detected_junction = j

    if not detected_junction:
        return {
            "status": "OUT_OF_ZONE",
            "message": "User is not currently in any junction detection perimeter.",
            "distance_to_nearest": round(min_dist, 1) if min_dist != float("inf") else None,
        }

    j_dict = detected_junction.model_dump() if hasattr(detected_junction, "model_dump") else dict(detected_junction)
    j_id = detected_junction.id if hasattr(detected_junction, "id") else detected_junction["id"]
    j_code = detected_junction.junction_code if hasattr(detected_junction, "junction_code") else detected_junction["junction_code"]
    j_name = detected_junction.name if hasattr(detected_junction, "name") else detected_junction["name"]

    # Record observation
    obs_result = traffic_service.record_user_ping(
        user_id=user_id,
        junction=j_dict,
        user_lat=ping.latitude,
        user_lon=ping.longitude,
        speed_kmh=ping.speed_kmh,
        is_emergency=ping.is_emergency,
    )

    # Update virtual signal state machine
    controller = signal_manager.get_or_create(
        junction_id=j_id,
        junction_code=j_code,
    )
    controller.update_tick()

    # Generate personalized in-car advisory
    advisory = None
    if obs_result:
        advisory = controller.generate_advisory_for_user(
            corridor=obs_result["corridor"],
            distance_meters=obs_result["distance_meters"],
        )

    # Broadcast update asynchronously
    await ws_manager.broadcast_junction_update(
        junction_id=j_id,
        data={
            "type": "TRAFFIC_UPDATE",
            "junction_id": j_id,
            "signal_state": controller.to_schema().model_dump(),
            "corridors": {
                c.value: traffic_service.get_corridor_summaries(j_id)[c].model_dump()
                for c in traffic_service.get_corridor_summaries(j_id)
            },
        },
    )

    return {
        "status": "IN_ZONE",
        "junction_id": j_id,
        "junction_name": j_name,
        "observation": obs_result,
        "advisory": advisory.model_dump() if advisory else None,
    }


@router.get("/{junction_id}", response_model=JunctionTrafficStatus)
async def get_junction_traffic_status(junction_id: str):
    j = await get_junction(junction_id)
    j_id = j.id if hasattr(j, "id") else j["id"]
    j_code = j.junction_code if hasattr(j, "junction_code") else j["junction_code"]
    j_name = j.name if hasattr(j, "name") else j["name"]
    summaries = traffic_service.get_corridor_summaries(j_id)
    total_vehicles = sum(s.vehicle_count for s in summaries.values())

    return JunctionTrafficStatus(
        junction_id=j_id,
        junction_code=j_code,
        name=j_name,
        total_participating_vehicles=total_vehicles,
        corridors={k.value: v for k, v in summaries.items()},
        last_updated=datetime.utcnow(),
    )


@router.get("/{junction_id}/participants")
async def get_junction_participants(junction_id: str):
    j = await get_junction(junction_id)
    j_id = j.id if hasattr(j, "id") else j["id"]
    return {
        "junction_id": j_id,
        "participants": traffic_service.get_active_participants_list(j_id),
    }

