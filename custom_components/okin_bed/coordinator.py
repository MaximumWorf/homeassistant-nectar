"""Coordinator for OKIN Bed integration."""

import asyncio
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from okin_bed import OkinBed

from .const import DOMAIN, CONF_MAC_ADDRESS, MODE_DIRECT, MODE_REMOTE

_LOGGER = logging.getLogger(__name__)


class OkinBedCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the OKIN bed."""

    def __init__(
        self,
        hass: HomeAssistant,
        mac_address: str,
        device_name: str,
        connection_mode: str = MODE_DIRECT,
        api_url: str | None = None,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{device_name}",
        )
        self.mac_address = mac_address
        self.device_name = device_name
        self.connection_mode = connection_mode
        self.api_url = api_url
        self.bed = None
        self._connected = False
        self._lock = asyncio.Lock()
        self._active_movements: dict[str, asyncio.Task] = {}

        # Only create bed instance in direct mode
        if connection_mode == MODE_DIRECT:
            self.bed = OkinBed(mac_address=mac_address)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from bed."""
        # OKIN beds don't provide position feedback
        # This is just a placeholder for future state tracking
        return {}

    async def async_connect(self) -> bool:
        """Ensure bed is connected."""
        async with self._lock:
            if self._connected:
                return True

            try:
                if self.connection_mode == MODE_DIRECT:
                    await self.bed.connect()
                    self._connected = True
                    _LOGGER.info("Connected to OKIN bed: %s", self.device_name)
                elif self.connection_mode == MODE_REMOTE:
                    # Test API connection
                    session = async_get_clientsession(self.hass)
                    async with session.get(f"{self.api_url}/health") as resp:
                        if resp.status == 200:
                            self._connected = True
                            _LOGGER.info("Connected to remote OKIN bed API: %s", self.api_url)
                        else:
                            raise Exception(f"API health check failed: {resp.status}")
                return True
            except Exception as err:
                _LOGGER.error("Failed to connect to bed: %s", err)
                self._connected = False
                return False

    async def async_disconnect(self) -> None:
        """Disconnect from bed."""
        async with self._lock:
            if not self._connected:
                return

            try:
                # Cancel any active movements
                for task in self._active_movements.values():
                    if not task.done():
                        task.cancel()
                self._active_movements.clear()

                if self.connection_mode == MODE_DIRECT and self.bed:
                    await self.bed.disconnect()

                self._connected = False
                _LOGGER.info("Disconnected from OKIN bed: %s", self.device_name)
            except Exception as err:
                _LOGGER.error("Error disconnecting from bed: %s", err)

    async def async_send_command(self, command_name: str) -> bool:
        """Send a single command to the bed."""
        if not await self.async_connect():
            return False

        try:
            if self.connection_mode == MODE_DIRECT:
                # Get the method from the OkinBed class
                command_method = getattr(self.bed, command_name, None)
                if command_method is None:
                    _LOGGER.error("Unknown command: %s", command_name)
                    return False

                await command_method()
                _LOGGER.debug("Sent command: %s", command_name)
                return True

            elif self.connection_mode == MODE_REMOTE:
                # Map command name to API endpoint
                endpoint = self._map_command_to_endpoint(command_name)
                if not endpoint:
                    _LOGGER.error("Unknown command for remote mode: %s", command_name)
                    return False

                # Send HTTP POST request with MAC address query parameter
                session = async_get_clientsession(self.hass)
                url = f"{self.api_url}{endpoint}?mac={self.mac_address}"
                async with session.post(url) as resp:
                    if resp.status == 200:
                        _LOGGER.debug("Sent remote command: %s to %s", command_name, self.mac_address)
                        return True
                    else:
                        _LOGGER.error("Remote command failed: %s (status %s)", command_name, resp.status)
                        return False

        except Exception as err:
            _LOGGER.error("Failed to send command %s: %s", command_name, err)
            return False

    def _map_command_to_endpoint(self, command_name: str) -> str | None:
        """Map internal command name to API endpoint."""
        # Position controls
        if command_name == "head_up":
            return "/head/up"
        elif command_name == "head_down":
            return "/head/down"
        elif command_name == "lumbar_up":
            return "/lumbar/up"
        elif command_name == "lumbar_down":
            return "/lumbar/down"
        elif command_name == "foot_up":
            return "/foot/up"
        elif command_name == "foot_down":
            return "/foot/down"
        elif command_name == "stop":
            return "/stop"
        # Presets
        elif command_name == "flat":
            return "/preset/flat"
        elif command_name == "zero_gravity":
            return "/preset/zero-gravity"
        elif command_name == "anti_snore":
            return "/preset/anti-snore"
        elif command_name == "tv_position":
            return "/preset/tv"
        elif command_name == "lounge":
            return "/preset/lounge"
        # Massage
        elif command_name == "massage_on":
            return "/massage/on"
        elif command_name == "massage_off":
            return "/massage/off"
        # Lighting
        elif command_name == "light_on":
            return "/light/on"
        elif command_name == "light_off":
            return "/light/off"
        elif command_name == "light_toggle":
            return "/light/toggle"
        else:
            return None

    async def async_start_continuous_movement(
        self, movement_id: str, command_name: str, interval: float = 0.5
    ) -> None:
        """Start continuous movement by repeatedly sending commands.

        Args:
            movement_id: Unique identifier for this movement (e.g., "head_up")
            command_name: Method name to call on OkinBed (e.g., "head_up")
            interval: Time between command sends in seconds
        """
        # Cancel existing movement with this ID
        await self.async_stop_continuous_movement(movement_id)

        async def _continuous_send():
            """Repeatedly send command."""
            while True:
                try:
                    await self.async_send_command(command_name)
                    await asyncio.sleep(interval)
                except asyncio.CancelledError:
                    _LOGGER.debug("Continuous movement cancelled: %s", movement_id)
                    break
                except Exception as err:
                    _LOGGER.error("Error in continuous movement %s: %s", movement_id, err)
                    break

        task = self.hass.async_create_task(_continuous_send())
        self._active_movements[movement_id] = task
        _LOGGER.debug("Started continuous movement: %s", movement_id)

    async def async_stop_continuous_movement(self, movement_id: str) -> None:
        """Stop a continuous movement."""
        task = self._active_movements.pop(movement_id, None)
        if task and not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            _LOGGER.debug("Stopped continuous movement: %s", movement_id)

    async def async_stop_all_movements(self) -> None:
        """Stop all movements and send stop command."""
        # Cancel all active movement tasks
        for movement_id in list(self._active_movements.keys()):
            await self.async_stop_continuous_movement(movement_id)

        # Send stop command to bed
        await self.async_send_command("stop")
