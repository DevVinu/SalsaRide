from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from datetime import datetime
import uuid
from app.schemas.junction import JunctionCreate, JunctionUpdate, JunctionResponse
from app.database import db_manager
from app.services.geo_service import calculate_haversine_distance

router = APIRouter(prefix="/junctions", tags=["Junctions"])


@router.get("", response_model=List[JunctionResponse])
async def list_junctions():
    if db_manager.is_connected:
        cursor = db_manager.db.junctions.find({"is_active": True})
        junctions = await cursor.to_list(length=100)
        # normalize _id
        for j in junctions:
            if "_id" in j and "id" not in j:
                j["id"] = str(j["_id"])
        return junctions
    else:
        return [j for j in db_manager.in_memory_store["junctions"] if j.get("is_active", True)]


@router.get("/nearby", response_model=List[dict])
async def find_nearby_junctions(
    latitude: float = Query(..., ge=-90.0, le=90.0),
    longitude: float = Query(..., ge=-180.0, le=180.0),
    max_radius_meters: float = Query(5000.0, ge=100.0, le=50000.0),
):
    """Calculates distances to all junctions and returns those within max_radius_meters."""
    all_junctions = await list_junctions()
    nearby = []

    for j in all_junctions:
        j_lat = j.latitude if hasattr(j, "latitude") else j["latitude"]
        j_lon = j.longitude if hasattr(j, "longitude") else j["longitude"]
        j_radius = j.detection_radius_meters if hasattr(j, "detection_radius_meters") else j.get("detection_radius_meters", 500)
        j_dict = j.model_dump() if hasattr(j, "model_dump") else dict(j)

        dist = calculate_haversine_distance(latitude, longitude, j_lat, j_lon)
        if dist <= max_radius_meters:
            is_inside_detection = dist <= j_radius
            nearby.append({
                **j_dict,
                "distance_to_user_meters": dist,
                "is_inside_detection_zone": is_inside_detection,
            })

    nearby.sort(key=lambda x: x["distance_to_user_meters"])
    return nearby


@router.get("/{junction_id}", response_model=JunctionResponse)
async def get_junction(junction_id: str):
    if db_manager.is_connected:
        j = await db_manager.db.junctions.find_one({"id": junction_id})
        if not j:
            j = await db_manager.db.junctions.find_one({"junction_code": junction_id})
    else:
        j = next(
            (
                item
                for item in db_manager.in_memory_store["junctions"]
                if item["id"] == junction_id or item["junction_code"] == junction_id
            ),
            None,
        )

    if not j:
        raise HTTPException(status_code=404, detail="Junction not found")
    return j


@router.post("", response_model=JunctionResponse, status_code=status.HTTP_201_CREATED)
async def create_junction(junction_in: JunctionCreate):
    j_dict = junction_in.model_dump()
    j_dict["id"] = f"junc_{uuid.uuid4().hex[:10]}"
    j_dict["created_at"] = datetime.utcnow()
    # GeoJSON for 2dsphere indexing in MongoDB
    j_dict["location"] = {
        "type": "Point",
        "coordinates": [junction_in.longitude, junction_in.latitude]
    }

    if db_manager.is_connected:
        await db_manager.db.junctions.insert_one(j_dict)
    else:
        db_manager.in_memory_store["junctions"].append(j_dict)

    return j_dict


@router.put("/{junction_id}", response_model=JunctionResponse)
async def update_junction(junction_id: str, update_in: JunctionUpdate):
    j = await get_junction(junction_id)
    j_id = j.id if hasattr(j, "id") else j["id"]
    j_lat = j.latitude if hasattr(j, "latitude") else j["latitude"]
    j_lon = j.longitude if hasattr(j, "longitude") else j["longitude"]
    updates = {k: v for k, v in update_in.model_dump().items() if v is not None}

    if "latitude" in updates or "longitude" in updates:
        lat = updates.get("latitude", j_lat)
        lon = updates.get("longitude", j_lon)
        updates["location"] = {"type": "Point", "coordinates": [lon, lat]}

    if db_manager.is_connected:
        await db_manager.db.junctions.update_one({"id": j_id}, {"$set": updates})
        updated = await db_manager.db.junctions.find_one({"id": j_id})
    else:
        idx = next(
            i for i, item in enumerate(db_manager.in_memory_store["junctions"]) if item["id"] == j_id
        )
        db_manager.in_memory_store["junctions"][idx].update(updates)
        updated = db_manager.in_memory_store["junctions"][idx]

    return updated

