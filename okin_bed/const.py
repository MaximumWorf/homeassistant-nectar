"""Constants for the OKIN Bed integration."""

DOMAIN = "okin_bed"

# Configuration
CONF_MAC_ADDRESS = "mac_address"
CONF_DEVICE_NAME = "device_name"
CONF_CONNECTION_MODE = "connection_mode"
CONF_API_URL = "api_url"

# Connection modes
MODE_DIRECT = "direct"
MODE_REMOTE = "remote"

# BLE Service UUIDs
OKIN_SERVICE_UUID = "62741523-52F9-8864-B1AB-3B3A8D65950B"
OKIN_TX_CHAR_UUID = "62741525-52F9-8864-B1AB-3B3A8D65950B"
OKIN_RX_CHAR_UUID = "62741625-52F9-8864-B1AB-3B3A8D65950B"

# Device name patterns
DEVICE_NAME_PATTERNS = ["OKIN", "Adjustable", "Comfort", "Luxe"]

# Timeouts
CONNECTION_TIMEOUT = 30
SCAN_TIMEOUT = 10

# Movement timing
MOVEMENT_COMMAND_INTERVAL = 0.5  # Seconds between repeated commands for continuous movement

# Preset positions (button entities)
PRESET_FLAT = "flat"
PRESET_ZERO_GRAVITY = "zero_gravity"
PRESET_ANTI_SNORE = "anti_snore"
PRESET_TV = "tv"
PRESET_LOUNGE = "lounge"

PRESETS = {
    PRESET_FLAT: "Flat",
    PRESET_ZERO_GRAVITY: "Zero Gravity",
    PRESET_ANTI_SNORE: "Anti-Snore",
    PRESET_TV: "TV",
    PRESET_LOUNGE: "Lounge",
}

# Attributes
ATTR_POSITION = "position"
ATTR_WAVE = "wave"
ATTR_INTENSITY = "intensity"
