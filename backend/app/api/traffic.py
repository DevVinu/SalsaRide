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
        dist = calculate_haversine_distance(
            ping.latitude, ping.longitude, j.latitude, j.longitude
        )
        if dist <= j.detection_radius_meters and dist < min_dist:
            min_dist = dist
            detected_junction = j

    if not detected_junction:
        return {
            "status": "OUT_OF_ZONE",
            "message": "User is not currently in any junction detection perimeter.",
            "distance_to_nearest": round(min_dist, 1) if min_dist != float("inf") else None,
        }

    # Record observation
    obs_result = traffic_service.record_user_ping(
        user_id=user_id,
        junction=detected_junction.model_dump(),
        user_lat=ping.latitude,
        user_lon=ping.longitude,
        speed_kmh=ping.speed_kmh,
        is_emergency=ping.is_emergency,
    )

    # Update virtual signal state machine
    controller = signal_manager.get_or_create(
        junction_id=detected_junction.id,
        junction_code=detected_junction.junction_code,
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
        junction_id=detected_junction.id,
        data={
            "type": "TRAFFIC_UPDATE",
            "junction_id": detected_junction.id,
            "signal_state": controller.to_schema().model_dump(),
            "corridors": {
                c.value: traffic_service.get_corridor_summaries(detected_junction.id)[c].model_dump()
                for c in traffic_service.get_corridor_summaries(detected_junction.id)
            },
        },
    )

    return {
        "status": "IN_ZONE",
        "junction_id": detected_junction.id,
        "junction_name": detected_junction.name,
        "observation": obs_result,
        "advisory": advisory.model_dump() if advisory else None,
    }


@router.get("/{junction_id}", response_model=JunctionTrafficStatus)
async def get_junction_traffic_status(junction_id: str):
    j = await get_junction(junction_id)
    summaries = traffic_service.get_corridor_summaries(j.id)
    total_vehicles = sum(s.vehicle_count for s in summaries.values())

    return JunctionTrafficStatus(
        junction_id=j.id,
        junction_code=j.junction_code,
        name=j.name,
        total_participating_vehicles=total_vehicles,
        corridors={k.value: v for k, v in summaries.items()},
        last_updated=datetime.utcnow(),
    )


@router.get("/{junction_id}/participants")
async def get_junction_participants(junction_id: str):
    j = await get_junction(junction_id)
    return {
        "junction_id": j.id,
        "participants": traffic_service.get_active_participants_list(j.id),
    }

