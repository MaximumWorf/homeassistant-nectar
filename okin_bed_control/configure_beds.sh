#!/bin/bash
# Configure bed MAC addresses for auto-connect on startup

set -e

CONFIG_DIR="/etc/okin-bed"
CONFIG_FILE="$CONFIG_DIR/config.env"

echo "========================================="
echo "OKIN Bed Auto-Connect Configuration"
echo "========================================="
echo ""

# Check if config directory exists, create if needed
if [ ! -d "$CONFIG_DIR" ]; then
    echo "Creating config directory..."
    sudo mkdir -p "$CONFIG_DIR"
fi

# Scan for beds
echo "Scanning for OKIN beds..."
echo "(This may take 10-15 seconds)"
echo ""

# Check if okin-bed-scanner is available
if command -v okin-bed-scanner &> /dev/null; then
    okin-bed-scanner || true
else
    echo "Scanner not found, skipping auto-detection"
fi

echo ""
echo "Enter bed MAC addresses (comma-separated for multiple beds)"
echo "Example for split king: AA:BB:CC:DD:EE:FF,11:22:33:44:55:66"
echo "Example for single bed: AA:BB:CC:DD:EE:FF"
echo ""
read -p "Bed MAC addresses: " BED_MACS

if [ -z "$BED_MACS" ]; then
    echo "ERROR: At least one MAC address is required"
    exit 1
fi

# Create config file
echo "Creating configuration file..."
sudo tee "$CONFIG_FILE" > /dev/null << EOF
# OKIN Bed API Server Configuration
# Generated: $(date)

# Comma-separated list of bed MAC addresses
OKIN_BED_MACS="$BED_MACS"

# Auto-connect on startup
OKIN_AUTO_CONNECT=true
EOF

# Update systemd service to use config file
SERVICE_FILE="/etc/systemd/system/okin-bed-server.service"

if [ -f "$SERVICE_FILE" ]; then
    echo "Updating systemd service to use config file..."

    # Check if EnvironmentFile is already present
    if ! grep -q "EnvironmentFile" "$SERVICE_FILE"; then
        sudo sed -i '/\[Service\]/a EnvironmentFile=/etc/okin-bed/config.env' "$SERVICE_FILE"
        sudo systemctl daemon-reload
        echo "✓ Service updated"
    else
        echo "✓ Service already configured"
    fi
fi

echo ""
echo "========================================="
echo "Configuration Complete!"
echo "========================================="
echo ""
echo "Configured beds: $BED_MACS"
echo "Config file: $CONFIG_FILE"
echo ""
echo "To apply changes, restart the service:"
echo "  sudo systemctl restart okin-bed-server"
echo ""
echo "To view configuration:"
echo "  cat $CONFIG_FILE"
echo ""
echo "To edit configuration:"
echo "  sudo nano $CONFIG_FILE"
echo ""
