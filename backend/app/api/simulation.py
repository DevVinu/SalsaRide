from fastapi import APIRouter, HTTPException, Query, status
from typing import Dict, Any
from app.schemas.traffic import SimulatedVehicleInject
from app.services.simulation_service import simulation_service
from app.services.traffic_service import traffic_service
from app.services.signal_controller import signal_manager
from app.api.junctions import get_junction
from app.websockets.connection_manager import ws_manager

router = APIRouter(prefix="/simulation", tags=["Simulation Engine"])


@router.post("/{junction_id}/inject")
async def inject_simulated_vehicle(junction_id: str, payload: SimulatedVehicleInject):
    j = await get_junction(junction_id)
    j_dict = j.model_dump() if hasattr(j, "model_dump") else dict(j)
    j_id = j.id if hasattr(j, "id") else j["id"]
    j_code = j.junction_code if hasattr(j, "junction_code") else j["junction_code"]

    result = simulation_service.inject_simulated_vehicle(
        junction=j_dict,
        corridor=payload.corridor,
        distance_fraction=payload.distance_fraction,
        speed_kmh=payload.speed_kmh,
        is_emergency=payload.is_emergency,
        waiting_seconds=payload.waiting_seconds,
    )

    controller = signal_manager.get_or_create(j_id, j_code)
    controller.update_tick()

    # Broadcast update
    await ws_manager.broadcast_junction_update(
        junction_id=j_id,
        data={
            "type": "SIMULATION_INJECT",
            "junction_id": j_id,
            "vehicle": result,
            "signal_state": controller.to_schema().model_dump(),
        },
    )

    return result


@router.post("/{junction_id}/preset")
async def apply_simulation_preset(
    junction_id: str,
    preset: str = Query(..., description="morning_rush | evening_rush | bottleneck | balanced | emergency"),
):
    j = await get_junction(junction_id)
    j_dict = j.model_dump() if hasattr(j, "model_dump") else dict(j)
    j_id = j.id if hasattr(j, "id") else j["id"]
    j_code = j.junction_code if hasattr(j, "junction_code") else j["junction_code"]

    result = simulation_service.apply_scenario_preset(junction=j_dict, preset_name=preset)

    controller = signal_manager.get_or_create(j_id, j_code)
    controller.update_tick()

    await ws_manager.broadcast_junction_update(
        junction_id=j_id,
        data={
            "type": "PRESET_APPLIED",
            "junction_id": j_id,
            "preset": preset,
            "signal_state": controller.to_schema().model_dump(),
        },
    )

    return result


@router.delete("/{junction_id}/clear")
async def clear_simulation(junction_id: str):
    j = await get_junction(junction_id)
    j_id = j.id if hasattr(j, "id") else j["id"]
    j_code = j.junction_code if hasattr(j, "junction_code") else j["junction_code"]
    j_name = j.name if hasattr(j, "name") else j.get("name", j_id)
    traffic_service.clear_junction_participants(j_id)

    controller = signal_manager.get_or_create(j_id, j_code)
    controller.update_tick()

    await ws_manager.broadcast_junction_update(
        junction_id=j_id,
        data={"type": "SIMULATION_CLEARED", "junction_id": j_id},
    )

    return {"status": "SUCCESS", "message": f"All simulated vehicles cleared for {j_name}"}

