"""Constants for OKIN Bed BLE protocol."""

from enum import Enum

# BLE Service UUIDs
OKIN_SERVICE_UUID = "62741523-52F9-8864-B1AB-3B3A8D65950B"
NUS_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"

# BLE Characteristic UUIDs - OKIN Custom
OKIN_TX_CHAR_UUID = "62741525-52F9-8864-B1AB-3B3A8D65950B"  # Write to bed
OKIN_RX_CHAR_UUID = "62741625-52F9-8864-B1AB-3B3A8D65950B"  # Read from bed

# BLE Characteristic UUIDs - Nordic UART Service
NUS_TX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Write
NUS_RX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Read/Notify

# Alternative service/characteristic UUIDs found in app
ALT_SERVICE_UUID_1 = "00001000-0000-1000-8000-00805f9b34fb"
ALT_SERVICE_UUID_2 = "0000ffe0-0000-1000-8000-00805f9b34fb"
ALT_CHAR_UUID_1 = "00001001-0000-1000-8000-00805f9b34fb"
ALT_CHAR_UUID_2 = "00001002-0000-1000-8000-00805f9b34fb"
ALT_CHAR_UUID_3 = "0000ffe9-0000-1000-8000-00805f9b34fb"
ALT_CHAR_UUID_4 = "0000ffe4-0000-1000-8000-00805f9b34fb"
ALT_CHAR_UUID_5 = "0000ffe5-0000-1000-8000-00805f9b34fb"

# CCCD UUID (for enabling notifications)
CCCD_UUID = "00002902-0000-1000-8000-00805f9b34fb"

# Device name patterns to look for
DEVICE_NAME_PATTERNS = [
    "OKIN",
    "Adjustable",
    "Comfort",
    "Luxe",
]

# Command bytes - captured and confirmed from BLE traffic
class Command:
    """Command byte constants - tested and verified."""
    # Position control
    HEAD_UP = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x00, 0xa5])
    HEAD_DOWN = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x01, 0xa5])
    LUMBAR_UP = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x04, 0xa5])
    LUMBAR_DOWN = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x07, 0xa5])
    FOOT_UP = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x02, 0xa5])
    FOOT_DOWN = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x03, 0xa5])
    STOP = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x0f, 0xa5])

    # Presets
    FLAT = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x10, 0xa5])
    ZERO_GRAVITY = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x13, 0xa5])
    LOUNGE = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x11, 0xa5])  # TV mode
    ANTI_SNORE = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x16, 0xa5])
    ASCENT = bytes([0x00])  # NOT YET CAPTURED

    # Massage
    MASSAGE_ON = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x58, 0xa5])
    MASSAGE_OFF = bytes([0x00])  # NOT YET CAPTURED
    MASSAGE_WAVE_1 = bytes([0x00])  # NOT YET CAPTURED
    MASSAGE_WAVE_2 = bytes([0x00])  # NOT YET CAPTURED
    MASSAGE_WAVE_3 = bytes([0x00])  # NOT YET CAPTURED

    # Lighting
    LIGHT_ON = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x73, 0xa5])
    LIGHT_OFF = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x74, 0xa5])
    LIGHT_TOGGLE = bytes([0x00])  # NOT YET CAPTURED
    BRIGHTNESS_UP = bytes([0x00])  # NOT YET CAPTURED
    BRIGHTNESS_DOWN = bytes([0x00])  # NOT YET CAPTURED

    # Unknown commands
    UNKNOWN_6F = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x6f, 0xa5])  # Does nothing
    UNKNOWN_SPECIAL = bytes([0x5a, 0xb0, 0x00, 0xa5])  # Not tested


class BedPosition(Enum):
    """Preset bed positions."""
    FLAT = "flat"
    ZERO_GRAVITY = "zero_gravity"
    LOUNGE = "lounge"
    ANTI_SNORE = "anti_snore"
    ASCENT = "ascent"


class MassageWave(Enum):
    """Massage wave patterns."""
    WAVE_1 = 1
    WAVE_2 = 2
    WAVE_3 = 3


class LightState(Enum):
    """Light states."""
    OFF = 0
    ON = 1


# Timeouts and delays
CONNECTION_TIMEOUT = 30.0  # seconds
COMMAND_DELAY = 0.1  # seconds between commands
SCAN_TIMEOUT = 10.0  # seconds for device scanning
