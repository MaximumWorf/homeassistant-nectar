"""Main OkinBed class for controlling the adjustable bed."""

import asyncio
import logging
from typing import Optional, Callable
from bleak import BleakClient, BleakScanner
from bleak.backends.device import BLEDevice

from .constants import (
    OKIN_SERVICE_UUID,
    OKIN_TX_CHAR_UUID,
    OKIN_RX_CHAR_UUID,
    NUS_TX_CHAR_UUID,
    NUS_RX_CHAR_UUID,
    DEVICE_NAME_PATTERNS,
    CONNECTION_TIMEOUT,
    COMMAND_DELAY,
    SCAN_TIMEOUT,
    Command,
    BedPosition,
    MassageWave,
)

logger = logging.getLogger(__name__)


class OkinBed:
    """Controller for OKIN adjustable bed via BLE."""

    def __init__(
        self,
        mac_address: Optional[str] = None,
        device_name: Optional[str] = None,
    ):
        """
        Initialize the OKIN bed controller.

        Args:
            mac_address: Bluetooth MAC address of the bed (optional)
            device_name: Name of the Bluetooth device (optional)
        """
        self.mac_address = mac_address
        self.device_name = device_name
        self.client: Optional[BleakClient] = None
        self.tx_char_uuid: Optional[str] = None
        self.rx_char_uuid: Optional[str] = None
        self._notification_callback: Optional[Callable] = None
        self._connected = False

    async def scan_for_bed(self, timeout: float = SCAN_TIMEOUT) -> Optional[BLEDevice]:
        """
        Scan for OKIN bed devices.

        Args:
            timeout: Scan timeout in seconds

        Returns:
            BLEDevice if found, None otherwise
        """
        logger.info("Scanning for OKIN bed devices...")

        def match_device(device: BLEDevice, _) -> bool:
            """Check if device matches OKIN bed patterns."""
            if not device.name:
                return False

            # Check if MAC address matches (if specified)
            if self.mac_address and device.address.lower() == self.mac_address.lower():
                return True

            # Check if name matches (if specified)
            if self.device_name and self.device_name.lower() in device.name.lower():
                return True

            # Check if name matches known patterns
            return any(pattern.lower() in device.name.lower() for pattern in DEVICE_NAME_PATTERNS)

        device = await BleakScanner.find_device_by_filter(match_device, timeout=timeout)

        if device:
            logger.info(f"Found bed device: {device.name} ({device.address})")
            self.mac_address = device.address
        else:
            logger.warning("No OKIN bed device found")

        return device

    async def connect(self, timeout: float = CONNECTION_TIMEOUT) -> bool:
        """
        Connect to the bed.

        Args:
            timeout: Connection timeout in seconds

        Returns:
            True if connected successfully, False otherwise
        """
        if self._connected:
            logger.warning("Already connected")
            return True

        # If no MAC address, try to find the device
        if not self.mac_address:
            device = await self.scan_for_bed()
            if not device:
                logger.error("Cannot connect: device not found")
                return False
            self.mac_address = device.address

        try:
            logger.info(f"Connecting to {self.mac_address}...")
            self.client = BleakClient(self.mac_address, timeout=timeout)
            await self.client.connect()

            if not self.client.is_connected:
                logger.error("Failed to connect")
                return False

            # Discover services and characteristics
            await self._discover_characteristics()

            self._connected = True
            logger.info("Connected successfully")
            return True

        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False

    async def _discover_characteristics(self):
        """Discover and set the correct TX/RX characteristics."""
        if not self.client:
            return

        # Try OKIN custom service first
        for service in self.client.services:
            if service.uuid.lower() == OKIN_SERVICE_UUID.lower():
                logger.info(f"Found OKIN service: {service.uuid}")
                self.tx_char_uuid = OKIN_TX_CHAR_UUID
                self.rx_char_uuid = OKIN_RX_CHAR_UUID
                return

        # Try Nordic UART Service
        for service in self.client.services:
            if service.uuid.lower() == NUS_TX_CHAR_UUID.lower()[:36]:  # Match service part
                logger.info(f"Found NUS service: {service.uuid}")
                self.tx_char_uuid = NUS_TX_CHAR_UUID
                self.rx_char_uuid = NUS_RX_CHAR_UUID
                return

        # If no known service found, log all available services
        logger.warning("No known service found. Available services:")
        for service in self.client.services:
            logger.warning(f"  Service: {service.uuid}")
            for char in service.characteristics:
                logger.warning(f"    Characteristic: {char.uuid} - {char.properties}")

        # Use first writable characteristic as fallback
        for service in self.client.services:
            for char in service.characteristics:
                if "write" in char.properties:
                    logger.info(f"Using fallback TX characteristic: {char.uuid}")
                    self.tx_char_uuid = char.uuid
                if "notify" in char.properties:
                    logger.info(f"Using fallback RX characteristic: {char.uuid}")
                    self.rx_char_uuid = char.uuid
            if self.tx_char_uuid:
                break

    async def disconnect(self):
        """Disconnect from the bed."""
        if self.client and self._connected:
            logger.info("Disconnecting...")
            await self.client.disconnect()
            self._connected = False
            logger.info("Disconnected")

    async def _send_command(self, command: bytes, response: bool = False) -> Optional[bytes]:
        """
        Send a command to the bed.

        Args:
            command: Command bytes to send
            response: Whether to wait for a response

        Returns:
            Response bytes if requested, None otherwise
        """
        if not self._connected or not self.client:
            logger.error("Not connected to bed")
            raise RuntimeError("Not connected to bed")

        if not self.tx_char_uuid:
            logger.error("TX characteristic not found")
            raise RuntimeError("TX characteristic not found")

        try:
            logger.debug(f"Sending command: {command.hex()}")
            await self.client.write_gatt_char(self.tx_char_uuid, command)
            await asyncio.sleep(COMMAND_DELAY)

            # TODO: Implement response handling if needed
            if response:
                logger.warning("Response handling not yet implemented")

            return None

        except Exception as e:
            logger.error(f"Error sending command: {e}")
            raise

    # Position control methods
    async def head_up(self):
        """Raise the head section."""
        await self._send_command(Command.HEAD_UP)

    async def head_down(self):
        """Lower the head section."""
        await self._send_command(Command.HEAD_DOWN)

    async def lumbar_up(self):
        """Raise the lumbar section."""
        await self._send_command(Command.LUMBAR_UP)

    async def lumbar_down(self):
        """Lower the lumbar section."""
        await self._send_command(Command.LUMBAR_DOWN)

    async def foot_up(self):
        """Raise the foot section."""
        await self._send_command(Command.FOOT_UP)

    async def foot_down(self):
        """Lower the foot section."""
        await self._send_command(Command.FOOT_DOWN)

    async def stop(self):
        """Stop all movement."""
        await self._send_command(Command.STOP)

    # Preset positions
    async def set_position(self, position: BedPosition):
        """
        Set bed to a preset position.

        Args:
            position: Desired bed position
        """
        command_map = {
            BedPosition.FLAT: Command.FLAT,
            BedPosition.ZERO_GRAVITY: Command.ZERO_GRAVITY,
            BedPosition.LOUNGE: Command.LOUNGE,
            BedPosition.ANTI_SNORE: Command.ANTI_SNORE,
            BedPosition.ASCENT: Command.ASCENT,
        }
        await self._send_command(command_map[position])

    async def flat(self):
        """Set bed to flat position."""
        await self.set_position(BedPosition.FLAT)

    async def zero_gravity(self):
        """Set bed to zero gravity position."""
        await self.set_position(BedPosition.ZERO_GRAVITY)

    async def lounge(self):
        """Set bed to lounge position."""
        await self.set_position(BedPosition.LOUNGE)

    async def anti_snore(self):
        """Set bed to anti-snore position."""
        await self.set_position(BedPosition.ANTI_SNORE)

    async def ascent(self):
        """Set bed to ascent position."""
        await self.set_position(BedPosition.ASCENT)

    # Massage control
    async def massage_on(self):
        """Turn massage on (wave 1)."""
        await self._send_command(Command.MASSAGE_ON)

    async def massage_off(self):
        """Turn massage off."""
        await self._send_command(Command.MASSAGE_OFF)

    async def set_massage_wave(self, wave: int):
        """
        Set massage wave pattern.

        Args:
            wave: Wave pattern (1, 2, or 3)
        """
        if wave not in [1, 2, 3]:
            raise ValueError("Wave must be 1, 2, or 3")

        command_map = {
            1: Command.MASSAGE_WAVE_1,
            2: Command.MASSAGE_WAVE_2,
            3: Command.MASSAGE_WAVE_3,
        }
        await self._send_command(command_map[wave])

    # Lighting control
    async def light_on(self):
        """Turn under-bed light on."""
        await self._send_command(Command.LIGHT_ON)

    async def light_off(self):
        """Turn under-bed light off."""
        await self._send_command(Command.LIGHT_OFF)

    async def light_toggle(self):
        """Toggle under-bed light."""
        await self._send_command(Command.LIGHT_TOGGLE)

    async def brightness_up(self):
        """Increase light brightness."""
        await self._send_command(Command.BRIGHTNESS_UP)

    async def brightness_down(self):
        """Decrease light brightness."""
        await self._send_command(Command.BRIGHTNESS_DOWN)

    # Context manager support
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
