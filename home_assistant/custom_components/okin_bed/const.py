"""Constants for the OKIN Bed integration."""

DOMAIN = "okin_bed"

# Configuration
CONF_MAC_ADDRESS = "mac_address"
CONF_DEVICE_NAME = "device_name"

# BLE Service UUIDs
OKIN_SERVICE_UUID = "62741523-52F9-8864-B1AB-3B3A8D65950B"
OKIN_TX_CHAR_UUID = "62741525-52F9-8864-B1AB-3B3A8D65950B"
OKIN_RX_CHAR_UUID = "62741625-52F9-8864-B1AB-3B3A8D65950B"

# Device name patterns
DEVICE_NAME_PATTERNS = ["OKIN", "Adjustable", "Comfort", "Luxe"]

# Timeouts
CONNECTION_TIMEOUT = 30
SCAN_TIMEOUT = 10

# Attributes
ATTR_POSITION = "position"
ATTR_WAVE = "wave"
ATTR_INTENSITY = "intensity"
