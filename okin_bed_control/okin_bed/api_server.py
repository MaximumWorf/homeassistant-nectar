"""REST API server for remote OKIN bed control over network.

This server runs on a Raspberry Pi with Bluetooth connectivity to the bed
and exposes HTTP endpoints for remote control from Home Assistant or other clients.
"""

import asyncio
import logging
import re
from typing import Optional, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Body, Query
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

# Global bed instances dictionary (keyed by MAC address)
bed_instances: Dict[str, OkinBed] = {}

# MAC address validation pattern
MAC_ADDRESS_PATTERN = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')


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


def validate_mac_address(mac: str) -> str:
    """Validate and normalize MAC address format."""
    if not MAC_ADDRESS_PATTERN.match(mac):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid MAC address format: {mac}. Expected format: XX:XX:XX:XX:XX:XX"
        )
    # Normalize to uppercase with colons
    return mac.upper().replace('-', ':')


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage bed connection lifecycle."""
    logger.info("OKIN Bed API Server starting...")
    yield
    # Cleanup on shutdown - disconnect all beds
    if bed_instances:
        logger.info(f"Disconnecting from {len(bed_instances)} bed(s)...")
        for mac, bed in bed_instances.items():
            if bed.client and bed.client.is_connected:
                logger.info(f"Disconnecting from bed {mac}")
                await bed.disconnect()
    logger.info("OKIN Bed API Server stopped")


app = FastAPI(
    title="OKIN Bed Control API",
    description="REST API for controlling OKIN adjustable beds via Bluetooth LE",
    version="1.0.0",
    lifespan=lifespan,
)


async def get_bed(mac_address: str) -> OkinBed:
    """Get or create bed instance for given MAC address.

    Maintains persistent connections to beds, creating new instances as needed.
    """
    global bed_instances

    # Validate and normalize MAC address
    mac = validate_mac_address(mac_address)

    # Get or create bed instance for this MAC
    if mac not in bed_instances:
        logger.info(f"Creating new bed instance for {mac}")
        bed_instances[mac] = OkinBed(mac_address=mac)

    bed = bed_instances[mac]

    # Ensure connection
    if not bed.client or not bed.client.is_connected:
        try:
            logger.info(f"Connecting to bed {mac}")
            await bed.connect()
        except Exception as e:
            logger.error(f"Failed to connect to bed {mac}: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Failed to connect to bed {mac}: {str(e)}"
            )

    return bed


@app.get("/")
async def root():
    """Root endpoint with API information."""
    connected_beds = {
        mac: (bed.client and bed.client.is_connected)
        for mac, bed in bed_instances.items()
    }
    return {
        "name": "OKIN Bed Control API",
        "version": "2.0.0",
        "status": "online",
        "connected_beds": connected_beds,
        "total_beds": len(bed_instances),
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "total_beds": len(bed_instances),
        "connected_beds": sum(1 for bed in bed_instances.values() if bed.client and bed.client.is_connected),
    }


@app.post("/config")
async def configure_bed(config: BedConfig):
    """Pre-configure a bed (creates instance but doesn't connect).

    Note: With multi-bed support, this endpoint is optional.
    Beds are auto-configured on first command.
    """
    global bed_instances

    mac = validate_mac_address(config.mac_address)

    if mac not in bed_instances:
        bed_instances[mac] = OkinBed(mac_address=mac)
        logger.info(f"Pre-configured bed: {mac}")

    return {
        "success": True,
        "message": f"Bed configured: {mac}",
        "mac_address": mac,
    }


@app.post("/connect")
async def connect(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Manually connect to bed."""
    bed = await get_bed(mac)
    return {
        "success": True,
        "message": "Connected to bed",
        "mac_address": bed.mac_address,
    }


@app.post("/disconnect")
async def disconnect(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Disconnect from specific bed."""
    global bed_instances

    mac_normalized = validate_mac_address(mac)

    if mac_normalized in bed_instances:
        bed = bed_instances[mac_normalized]
        if bed.client and bed.client.is_connected:
            await bed.disconnect()
            return {
                "success": True,
                "message": f"Disconnected from bed {mac_normalized}"
            }

    return {
        "success": True,
        "message": f"Bed {mac_normalized} already disconnected"
    }


# Position control endpoints
@app.post("/head/up", response_model=CommandResponse)
async def head_up(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Raise head section."""
    bed = await get_bed(mac)
    await bed.head_up()
    return CommandResponse(success=True, message="Head up", command="head_up")


@app.post("/head/down", response_model=CommandResponse)
async def head_down(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Lower head section."""
    bed = await get_bed(mac)
    await bed.head_down()
    return CommandResponse(success=True, message="Head down", command="head_down")


@app.post("/lumbar/up", response_model=CommandResponse)
async def lumbar_up(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Raise lumbar section."""
    bed = await get_bed(mac)
    await bed.lumbar_up()
    return CommandResponse(success=True, message="Lumbar up", command="lumbar_up")


@app.post("/lumbar/down", response_model=CommandResponse)
async def lumbar_down(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Lower lumbar section."""
    bed = await get_bed(mac)
    await bed.lumbar_down()
    return CommandResponse(success=True, message="Lumbar down", command="lumbar_down")


@app.post("/foot/up", response_model=CommandResponse)
async def foot_up(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Raise foot section."""
    bed = await get_bed(mac)
    await bed.foot_up()
    return CommandResponse(success=True, message="Foot up", command="foot_up")


@app.post("/foot/down", response_model=CommandResponse)
async def foot_down(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Lower foot section."""
    bed = await get_bed(mac)
    await bed.foot_down()
    return CommandResponse(success=True, message="Foot down", command="foot_down")


@app.post("/stop", response_model=CommandResponse)
async def stop(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Stop all movement."""
    bed = await get_bed(mac)
    await bed.stop()
    return CommandResponse(success=True, message="Stopped", command="stop")


# Preset positions
@app.post("/preset/flat", response_model=CommandResponse)
async def preset_flat(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Move to flat position."""
    bed = await get_bed(mac)
    await bed.flat()
    return CommandResponse(success=True, message="Flat position", command="flat")


@app.post("/preset/zero-gravity", response_model=CommandResponse)
async def preset_zero_gravity(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Move to zero gravity position."""
    bed = await get_bed(mac)
    await bed.zero_gravity()
    return CommandResponse(success=True, message="Zero gravity", command="zero_gravity")


@app.post("/preset/anti-snore", response_model=CommandResponse)
async def preset_anti_snore(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Move to anti-snore position."""
    bed = await get_bed(mac)
    await bed.anti_snore()
    return CommandResponse(success=True, message="Anti-snore", command="anti_snore")


@app.post("/preset/tv", response_model=CommandResponse)
async def preset_tv(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Move to TV position."""
    bed = await get_bed(mac)
    await bed.tv_position()
    return CommandResponse(success=True, message="TV position", command="tv_position")


@app.post("/preset/lounge", response_model=CommandResponse)
async def preset_lounge(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Move to lounge position."""
    bed = await get_bed(mac)
    await bed.lounge()
    return CommandResponse(success=True, message="Lounge", command="lounge")


# Massage controls
@app.post("/massage/on", response_model=CommandResponse)
async def massage_on(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Turn massage on."""
    bed = await get_bed(mac)
    await bed.massage_on()
    return CommandResponse(success=True, message="Massage on", command="massage_on")


@app.post("/massage/off", response_model=CommandResponse)
async def massage_off(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Turn massage off."""
    bed = await get_bed(mac)
    await bed.massage_off()
    return CommandResponse(success=True, message="Massage off", command="massage_off")


# Lighting controls
@app.post("/light/on", response_model=CommandResponse)
async def light_on(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Turn under-bed light on."""
    bed = await get_bed(mac)
    await bed.light_on()
    return CommandResponse(success=True, message="Light on", command="light_on")


@app.post("/light/off", response_model=CommandResponse)
async def light_off(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Turn under-bed light off."""
    bed = await get_bed(mac)
    await bed.light_off()
    return CommandResponse(success=True, message="Light off", command="light_off")


@app.post("/light/toggle", response_model=CommandResponse)
async def light_toggle(mac: str = Query(..., description="Bluetooth MAC address of the bed")):
    """Toggle under-bed light."""
    bed = await get_bed(mac)
    await bed.light_toggle()
    return CommandResponse(success=True, message="Light toggled", command="light_toggle")


def main():
    """Main entry point for the API server."""
    import uvicorn
    import argparse

    global bed_instances

    parser = argparse.ArgumentParser(
        description="OKIN Bed API Server - Multi-bed support via MAC query parameter"
    )
    parser.add_argument(
        "--mac",
        type=str,
        help="(Optional) Pre-configure a bed MAC address. With multi-bed support, "
             "MAC addresses can be provided via query parameters instead.",
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

    # Pre-configure bed if MAC provided (backward compatibility)
    if args.mac:
        mac = validate_mac_address(args.mac)
        bed_instances[mac] = OkinBed(mac_address=mac)
        logger.info(f"Pre-configured bed MAC: {mac}")
    else:
        logger.info("No pre-configured MAC. Beds will be configured via query parameters.")

    logger.info(f"Starting OKIN Bed API server on {args.host}:{args.port}")
    logger.info("Multi-bed mode: Use ?mac=XX:XX:XX:XX:XX:XX on all endpoints")

    uvicorn.run(
        "okin_bed.api_server:app",
        host=args.host,
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
