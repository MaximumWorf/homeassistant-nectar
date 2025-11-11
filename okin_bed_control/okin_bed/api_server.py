"""REST API server for remote OKIN bed control over network.

This server runs on a Raspberry Pi with Bluetooth connectivity to the bed
and exposes HTTP endpoints for remote control from Home Assistant or other clients.
"""

import asyncio
import logging
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from .bed import OkinBed
from .constants import MassageWave

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global bed instance
bed_instance: Optional[OkinBed] = None
bed_mac_address: Optional[str] = None


class BedConfig(BaseModel):
    """Bed configuration."""
    mac_address: str = Field(..., description="Bluetooth MAC address of the bed")


class MassageConfig(BaseModel):
    """Massage configuration."""
    wave: str = Field(..., description="Massage wave pattern")
    intensity: int = Field(1, ge=1, le=10, description="Massage intensity (1-10)")


class CommandResponse(BaseModel):
    """Standard command response."""
    success: bool
    message: str
    command: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage bed connection lifecycle."""
    logger.info("OKIN Bed API Server starting...")
    yield
    # Cleanup on shutdown
    if bed_instance and bed_instance.is_connected:
        logger.info("Disconnecting from bed...")
        await bed_instance.disconnect()
    logger.info("OKIN Bed API Server stopped")


app = FastAPI(
    title="OKIN Bed Control API",
    description="REST API for controlling OKIN adjustable beds via Bluetooth LE",
    version="1.0.0",
    lifespan=lifespan,
)


async def get_bed() -> OkinBed:
    """Get or create bed instance."""
    global bed_instance, bed_mac_address

    if bed_instance is None:
        if bed_mac_address is None:
            raise HTTPException(
                status_code=503,
                detail="Bed not configured. POST to /config first."
            )
        bed_instance = OkinBed(mac_address=bed_mac_address)

    # Ensure connection
    if not bed_instance.is_connected:
        try:
            await bed_instance.connect()
        except Exception as e:
            logger.error(f"Failed to connect to bed: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Failed to connect to bed: {str(e)}"
            )

    return bed_instance


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "OKIN Bed Control API",
        "version": "1.0.0",
        "status": "online",
        "bed_connected": bed_instance.is_connected if bed_instance else False,
        "bed_mac": bed_mac_address,
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "bed_connected": bed_instance.is_connected if bed_instance else False,
    }


@app.post("/config")
async def configure_bed(config: BedConfig):
    """Configure the bed MAC address."""
    global bed_instance, bed_mac_address

    bed_mac_address = config.mac_address
    bed_instance = None  # Reset instance to pick up new config

    logger.info(f"Configured bed MAC address: {bed_mac_address}")

    return {
        "success": True,
        "message": f"Bed configured: {bed_mac_address}",
        "mac_address": bed_mac_address,
    }


@app.post("/connect")
async def connect():
    """Manually connect to bed."""
    bed = await get_bed()
    return {
        "success": True,
        "message": "Connected to bed",
        "mac_address": bed.mac_address,
    }


@app.post("/disconnect")
async def disconnect():
    """Disconnect from bed."""
    global bed_instance

    if bed_instance and bed_instance.is_connected:
        await bed_instance.disconnect()
        return {
            "success": True,
            "message": "Disconnected from bed"
        }

    return {
        "success": True,
        "message": "Already disconnected"
    }


# Position control endpoints
@app.post("/head/up", response_model=CommandResponse)
async def head_up():
    """Raise head section."""
    bed = await get_bed()
    await bed.head_up()
    return CommandResponse(success=True, message="Head up", command="head_up")


@app.post("/head/down", response_model=CommandResponse)
async def head_down():
    """Lower head section."""
    bed = await get_bed()
    await bed.head_down()
    return CommandResponse(success=True, message="Head down", command="head_down")


@app.post("/lumbar/up", response_model=CommandResponse)
async def lumbar_up():
    """Raise lumbar section."""
    bed = await get_bed()
    await bed.lumbar_up()
    return CommandResponse(success=True, message="Lumbar up", command="lumbar_up")


@app.post("/lumbar/down", response_model=CommandResponse)
async def lumbar_down():
    """Lower lumbar section."""
    bed = await get_bed()
    await bed.lumbar_down()
    return CommandResponse(success=True, message="Lumbar down", command="lumbar_down")


@app.post("/foot/up", response_model=CommandResponse)
async def foot_up():
    """Raise foot section."""
    bed = await get_bed()
    await bed.foot_up()
    return CommandResponse(success=True, message="Foot up", command="foot_up")


@app.post("/foot/down", response_model=CommandResponse)
async def foot_down():
    """Lower foot section."""
    bed = await get_bed()
    await bed.foot_down()
    return CommandResponse(success=True, message="Foot down", command="foot_down")


@app.post("/stop", response_model=CommandResponse)
async def stop():
    """Stop all movement."""
    bed = await get_bed()
    await bed.stop()
    return CommandResponse(success=True, message="Stopped", command="stop")


# Preset positions
@app.post("/preset/flat", response_model=CommandResponse)
async def preset_flat():
    """Move to flat position."""
    bed = await get_bed()
    await bed.flat()
    return CommandResponse(success=True, message="Flat position", command="flat")


@app.post("/preset/zero-gravity", response_model=CommandResponse)
async def preset_zero_gravity():
    """Move to zero gravity position."""
    bed = await get_bed()
    await bed.zero_gravity()
    return CommandResponse(success=True, message="Zero gravity", command="zero_gravity")


@app.post("/preset/anti-snore", response_model=CommandResponse)
async def preset_anti_snore():
    """Move to anti-snore position."""
    bed = await get_bed()
    await bed.anti_snore()
    return CommandResponse(success=True, message="Anti-snore", command="anti_snore")


@app.post("/preset/tv", response_model=CommandResponse)
async def preset_tv():
    """Move to TV position."""
    bed = await get_bed()
    await bed.tv_position()
    return CommandResponse(success=True, message="TV position", command="tv_position")


@app.post("/preset/lounge", response_model=CommandResponse)
async def preset_lounge():
    """Move to lounge position."""
    bed = await get_bed()
    await bed.lounge()
    return CommandResponse(success=True, message="Lounge", command="lounge")


# Massage controls
@app.post("/massage/on", response_model=CommandResponse)
async def massage_on():
    """Turn massage on."""
    bed = await get_bed()
    await bed.massage_on()
    return CommandResponse(success=True, message="Massage on", command="massage_on")


@app.post("/massage/off", response_model=CommandResponse)
async def massage_off():
    """Turn massage off."""
    bed = await get_bed()
    await bed.massage_off()
    return CommandResponse(success=True, message="Massage off", command="massage_off")


# Lighting controls
@app.post("/light/on", response_model=CommandResponse)
async def light_on():
    """Turn under-bed light on."""
    bed = await get_bed()
    await bed.light_on()
    return CommandResponse(success=True, message="Light on", command="light_on")


@app.post("/light/off", response_model=CommandResponse)
async def light_off():
    """Turn under-bed light off."""
    bed = await get_bed()
    await bed.light_off()
    return CommandResponse(success=True, message="Light off", command="light_off")


@app.post("/light/toggle", response_model=CommandResponse)
async def light_toggle():
    """Toggle under-bed light."""
    bed = await get_bed()
    await bed.light_toggle()
    return CommandResponse(success=True, message="Light toggled", command="light_toggle")


def main():
    """Main entry point for the API server."""
    import uvicorn
    import argparse

    global bed_mac_address

    parser = argparse.ArgumentParser(description="OKIN Bed API Server")
    parser.add_argument(
        "--mac",
        type=str,
        help="Bluetooth MAC address of the bed",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)",
    )

    args = parser.parse_args()

    # Set MAC address if provided
    if args.mac:
        bed_mac_address = args.mac
        logger.info(f"Pre-configured bed MAC: {bed_mac_address}")

    logger.info(f"Starting OKIN Bed API server on {args.host}:{args.port}")

    uvicorn.run(
        "okin_bed.api_server:app",
        host=args.host,
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
