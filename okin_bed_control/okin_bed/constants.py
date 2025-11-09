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

# Command bytes (placeholders - to be determined via packet capture)
# These will need to be reverse engineered from actual BLE traffic
class Command:
    """Command byte constants (to be populated via reverse engineering)."""
    # Position control
    HEAD_UP = bytes([0x00])  # Placeholder
    HEAD_DOWN = bytes([0x01])  # Placeholder
    LUMBAR_UP = bytes([0x02])  # Placeholder
    LUMBAR_DOWN = bytes([0x03])  # Placeholder
    FOOT_UP = bytes([0x04])  # Placeholder
    FOOT_DOWN = bytes([0x05])  # Placeholder
    STOP = bytes([0x06])  # Placeholder

    # Presets
    FLAT = bytes([0x10])  # Placeholder
    ZERO_GRAVITY = bytes([0x11])  # Placeholder
    LOUNGE = bytes([0x12])  # Placeholder
    ANTI_SNORE = bytes([0x13])  # Placeholder
    ASCENT = bytes([0x14])  # Placeholder

    # Massage
    MASSAGE_ON = bytes([0x20])  # Placeholder
    MASSAGE_OFF = bytes([0x21])  # Placeholder
    MASSAGE_WAVE_1 = bytes([0x22])  # Placeholder
    MASSAGE_WAVE_2 = bytes([0x23])  # Placeholder
    MASSAGE_WAVE_3 = bytes([0x24])  # Placeholder

    # Lighting
    LIGHT_ON = bytes([0x30])  # Placeholder
    LIGHT_OFF = bytes([0x31])  # Placeholder
    LIGHT_TOGGLE = bytes([0x32])  # Placeholder
    BRIGHTNESS_UP = bytes([0x33])  # Placeholder
    BRIGHTNESS_DOWN = bytes([0x34])  # Placeholder


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
