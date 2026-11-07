from fastapi import APIRouter, HTTPException, Query, status
from app.schemas.signal import VirtualSignalState, UserSignalAdvisory
from app.core.constants import Direction
from app.services.signal_controller import signal_manager
from app.api.junctions import get_junction
from app.websockets.connection_manager import ws_manager

router = APIRouter(prefix="/signals", tags=["Virtual Traffic Signals"])


@router.get("/{junction_id}", response_model=VirtualSignalState)
async def get_virtual_signal_state(junction_id: str):
    j = await get_junction(junction_id)
    j_id = j.id if hasattr(j, "id") else j["id"]
    j_code = j.junction_code if hasattr(j, "junction_code") else j["junction_code"]
    controller = signal_manager.get_or_create(junction_id=j_id, junction_code=j_code)
    controller.update_tick()
    return controller.to_schema()


@router.get("/{junction_id}/advisory", response_model=UserSignalAdvisory)
async def get_driver_advisory(
    junction_id: str,
    corridor: Direction = Query(...),
    distance_meters: float = Query(..., ge=0.0),
):
    j = await get_junction(junction_id)
    j_id = j.id if hasattr(j, "id") else j["id"]
    j_code = j.junction_code if hasattr(j, "junction_code") else j["junction_code"]
    controller = signal_manager.get_or_create(junction_id=j_id, junction_code=j_code)
    controller.update_tick()
    return controller.generate_advisory_for_user(corridor=corridor, distance_meters=distance_meters)


@router.post("/{junction_id}/step")
async def step_virtual_signal(junction_id: str):
    """Admin / Developer test tool: triggers immediate phase step."""
    j = await get_junction(junction_id)
    j_id = j.id if hasattr(j, "id") else j["id"]
    j_code = j.junction_code if hasattr(j, "junction_code") else j["junction_code"]
    controller = signal_manager.get_or_create(junction_id=j_id, junction_code=j_code)
    # Force phase expiration
    controller.phase_duration_seconds = controller.elapsed_seconds
    changed = controller.update_tick()

    state = controller.to_schema().model_dump()
    await ws_manager.broadcast_junction_update(
        junction_id=j_id,
        data={"type": "SIGNAL_STEP", "junction_id": j_id, "signal_state": state},
    )

    return {"status": "SUCCESS", "phase_changed": changed, "signal_state": state}

