import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, db_manager
from app.api import auth, junctions, traffic, signals, simulation
from app.websockets.connection_manager import ws_manager
from app.services.signal_controller import signal_manager
from app.services.traffic_service import traffic_service
from app.api.junctions import list_junctions

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("smartflow.main")

# Background Signal State Machine Tick Worker
async def signal_timer_background_task():
    logger.info("Starting SmartFlow virtual signal background timer loop...")
    while True:
        try:
            junctions_list = await list_junctions()
            for j in junctions_list:
                j_id = j.id if hasattr(j, "id") else j["id"]
                j_code = j.junction_code if hasattr(j, "junction_code") else j["junction_code"]
                controller = signal_manager.get_or_create(j_id, j_code)
                changed = controller.update_tick()
                
                # Broadcast every 1s tick or upon phase change
                summaries = traffic_service.get_corridor_summaries(j_id)
                await ws_manager.broadcast_junction_update(
                    junction_id=j_id,
                    data={
                        "type": "SIGNAL_TICK",
                        "junction_id": j_id,
                        "phase_changed": changed,
                        "signal_state": controller.to_schema().model_dump(),
                        "corridors": {c.value: summaries[c].model_dump() for c in summaries},
                    }
                )
        except Exception as e:
            logger.error(f"Error in signal timer background loop: {e}")
        await asyncio.sleep(1.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to DB and seed default junctions if empty
    await connect_to_mongo()
    
    # Initialize default urban intersections if store is empty
    existing = await list_junctions()
    if not existing:
        from app.schemas.junction import JunctionCreate
        from app.api.junctions import create_junction
        
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
            JunctionCreate(
                junction_code="SFO_MKT_04",
                name="Market St & 4th Central Ring",
                city="San Francisco",
                address="Market St & 4th St, San Francisco, CA",
                latitude=37.7857,
                longitude=-122.4064,
                detection_radius_meters=500,
                inner_zone_meters=150,
                mid_zone_meters=300,
            ),
            JunctionCreate(
                junction_code="CMB_GAL_03",
                name="Galle Road Colpetty Junction",
                city="Colombo",
                address="Galle Road & R.A. De Mel Mawatha, Colombo 03",
                latitude=6.9015,
                longitude=79.8517,
                detection_radius_meters=500,
                inner_zone_meters=150,
                mid_zone_meters=300,
            )
        ]
        for d in defaults:
            await create_junction(d)
        logger.info("Default SmartFlow urban junctions seeded.")

    # Start background signal ticker if enabled and not running under tests
    bg_task = None
    is_testing = os.getenv("TESTING", "false").lower() in ("true", "1") or "pytest" in sys.modules
    if not is_testing and os.getenv("ENABLE_BACKGROUND_TICKER", "true").lower() in ("true", "1"):
        bg_task = asyncio.create_task(signal_timer_background_task())

    try:
        yield
    finally:
        if bg_task:
            bg_task.cancel()
            try:
                await bg_task
            except asyncio.CancelledError:
                pass
        await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SmartFlow - AI-Powered GPS Intelligent Traffic Management System with Dynamic Virtual Signal Allocation.",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(junctions.router, prefix=settings.API_V1_STR)
app.include_router(traffic.router, prefix=settings.API_V1_STR)
app.include_router(signals.router, prefix=settings.API_V1_STR)
app.include_router(simulation.router, prefix=settings.API_V1_STR)

# Real-time WebSockets
@app.websocket("/ws/junctions/{junction_id}")
async def websocket_junction_endpoint(websocket: WebSocket, junction_id: str):
    await ws_manager.connect(websocket, junction_id=junction_id)
    try:
        while True:
            # Keep-alive receive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, junction_id=junction_id)

@app.websocket("/ws/admin")
async def websocket_admin_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket, junction_id=None)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, junction_id=None)

# Mount Admin Dashboard static files
admin_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "admin_dashboard"))
if os.path.exists(admin_dir):
    app.mount("/admin", StaticFiles(directory=admin_dir, html=True), name="admin")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>SmartFlow Traffic Management System API</title></head>
        <body style="font-family: sans-serif; background: #0f172a; color: #f8fafc; padding: 40px; text-align: center;">
            <h1 style="color: #38bdf8;">🚦 SmartFlow - AI-Powered Traffic Management System</h1>
            <p style="color: #94a3b8;">GPS-based dynamic virtual traffic signal allocation & simulation.</p>
            <div style="margin-top: 30px;">
                <a href="/docs" style="display: inline-block; background: #38bdf8; color: #0f172a; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; margin-right: 15px;">Interactive API Docs (Swagger)</a>
                <a href="/admin/" style="display: inline-block; background: #10b981; color: #0f172a; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold;">Launch Admin Dashboard</a>
            </div>
            <div style="margin-top: 50px; font-size: 12px; color: #64748b; border: 1px dashed #334155; padding: 15px; border-radius: 8px; max-width: 600px; margin-left: auto; margin-right: auto;">
                <strong>DISCLAIMER:</strong> SmartFlow is an informational virtual traffic advisory system. It does not replace or override actual municipal road signals.
            </div>
        </body>
    </html>
    """

