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
    result = simulation_service.inject_simulated_vehicle(
        junction=j.model_dump(),
        corridor=payload.corridor,
        distance_fraction=payload.distance_fraction,
        speed_kmh=payload.speed_kmh,
        is_emergency=payload.is_emergency,
        waiting_seconds=payload.waiting_seconds,
    )

    controller = signal_manager.get_or_create(j.id, j.junction_code)
    controller.update_tick()

    # Broadcast update
    await ws_manager.broadcast_junction_update(
        junction_id=j.id,
        data={
            "type": "SIMULATION_INJECT",
            "junction_id": j.id,
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
    result = simulation_service.apply_scenario_preset(junction=j.model_dump(), preset_name=preset)

    controller = signal_manager.get_or_create(j.id, j.junction_code)
    controller.update_tick()

    await ws_manager.broadcast_junction_update(
        junction_id=j.id,
        data={
            "type": "PRESET_APPLIED",
            "junction_id": j.id,
            "preset": preset,
            "signal_state": controller.to_schema().model_dump(),
        },
    )

    return result


@router.delete("/{junction_id}/clear")
async def clear_simulation(junction_id: str):
    j = await get_junction(junction_id)
    traffic_service.clear_junction_participants(j.id)

    controller = signal_manager.get_or_create(j.id, j.junction_code)
    controller.update_tick()

    await ws_manager.broadcast_junction_update(
        junction_id=j.id,
        data={"type": "SIMULATION_CLEARED", "junction_id": j.id},
    )

    return {"status": "SUCCESS", "message": f"All simulated vehicles cleared for {j.name}"}

