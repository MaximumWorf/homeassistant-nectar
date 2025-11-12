#!/bin/bash
# Quick install script for OKIN Bed BLE Controller
# Supports multiple beds on a single Raspberry Pi (perfect for split king!)
# Usage: curl -fsSL https://raw.githubusercontent.com/MaximumWorf/homeassistant-nectar/main/quick_install.sh | bash

set -e

echo "========================================="
echo "OKIN Bed BLE Controller - Quick Install"
echo "========================================="
echo ""

# Check if running on Raspberry Pi / Linux
if [[ ! "$OSTYPE" == "linux"* ]]; then
    echo "ERROR: This script is designed for Linux systems"
    exit 1
fi

# Check for existing installations
INSTALL_DIR="$HOME/okin-bed-control"
EXISTING_SERVICES=$(systemctl list-units --all "okin-bed-server-*" --no-legend 2>/dev/null | wc -l)

if [ $EXISTING_SERVICES -gt 0 ]; then
    echo "Found $EXISTING_SERVICES existing bed(s) configured"
    echo ""
    systemctl list-units --all "okin-bed-server-*" --no-legend | awk '{print "  - " $1}'
    echo ""
    read -p "Add another bed? (y/n): " ADD_ANOTHER </dev/tty
    if [[ ! "$ADD_ANOTHER" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled"
        exit 0
    fi
    BED_NUM=$((EXISTING_SERVICES + 1))
    DEFAULT_PORT=$((8000 + EXISTING_SERVICES))
else
    echo "This appears to be your first bed installation"
    BED_NUM=1
    DEFAULT_PORT=8000
fi

echo ""
echo "Configuring Bed #$BED_NUM"
echo "========================="

# Get bed MAC address
echo ""
echo "Enter the Bluetooth MAC address for Bed #$BED_NUM:"
echo "(Format: XX:XX:XX:XX:XX:XX)"
read -p "MAC Address: " BED_MAC </dev/tty

if [ -z "$BED_MAC" ]; then
    echo "ERROR: MAC address is required"
    exit 1
fi

# Get friendly name
read -p "Friendly name (e.g., 'Left Bed', 'Right Bed'): " BED_NAME </dev/tty
if [ -z "$BED_NAME" ]; then
    BED_NAME="Bed $BED_NUM"
fi

# Get port number
read -p "API Port (default: $DEFAULT_PORT): " API_PORT </dev/tty
API_PORT=${API_PORT:-$DEFAULT_PORT}

# Install system dependencies (skip if already installed)
if [ $BED_NUM -eq 1 ]; then
    echo ""
    echo "Installing system dependencies..."
    sudo apt-get update -qq
    sudo apt-get install -y python3 python3-pip python3-venv git bluez
fi

# Clone or update repository (skip if already exists)
if [ -d "$INSTALL_DIR" ]; then
    if [ $BED_NUM -gt 1 ]; then
        echo ""
        echo "Using existing installation..."
    else
        echo ""
        echo "Updating existing installation..."
        cd "$INSTALL_DIR"
        git pull
    fi
else
    echo ""
    echo "Cloning repository..."
    git clone https://github.com/MaximumWorf/homeassistant-nectar.git "$INSTALL_DIR"
fi

# Install Python package with server dependencies (skip if already installed)
if [ $BED_NUM -eq 1 ] || ! command -v okin-bed-server &> /dev/null; then
    echo ""
    echo "Installing Python package..."
    cd "$INSTALL_DIR/okin_bed_control"
    pip3 install --user -e ".[server]"
fi

# Create systemd service for this bed
echo ""
echo "Creating systemd service for $BED_NAME..."
SERVICE_NAME="okin-bed-server-$BED_NUM"
SERVICE_FILE="/tmp/${SERVICE_NAME}.service"
cat > $SERVICE_FILE << EOF
[Unit]
Description=OKIN Bed BLE API Server - $BED_NAME
After=network.target bluetooth.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME
Environment="PATH=$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$HOME/.local/bin/okin-bed-server --mac $BED_MAC --host 0.0.0.0 --port $API_PORT
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo cp $SERVICE_FILE /etc/systemd/system/${SERVICE_NAME}.service
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}.service

echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "Bed #$BED_NUM: $BED_NAME"
echo "MAC Address: $BED_MAC"
echo "API Port: $API_PORT"
echo "Service: $SERVICE_NAME"
echo "API URL: http://$(hostname -I | awk '{print $1}'):$API_PORT"
echo ""
echo "Commands:"
echo "  Start:   sudo systemctl start $SERVICE_NAME"
echo "  Stop:    sudo systemctl stop $SERVICE_NAME"
echo "  Status:  sudo systemctl status $SERVICE_NAME"
echo "  Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo ""

# Show all configured beds
if [ $BED_NUM -gt 1 ]; then
    echo "All Configured Beds:"
    echo "===================="
    for i in $(seq 1 $BED_NUM); do
        if systemctl list-units --all "okin-bed-server-$i.service" --no-legend 2>/dev/null | grep -q "okin-bed-server-$i"; then
            PORT=$((8000 + i - 1))
            echo "  Bed #$i: http://$(hostname -I | awk '{print $1}'):$PORT"
        fi
    done
    echo ""
fi

echo "Next steps:"
echo "1. Start the service: sudo systemctl start $SERVICE_NAME"
echo "2. Test: curl http://localhost:$API_PORT/health"
echo "3. Add to Home Assistant (Remote mode) using the API URL above"
if [ $BED_NUM -eq 1 ]; then
    echo "4. To add another bed (e.g., split king), run this script again!"
fi
echo ""
