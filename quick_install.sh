#!/bin/bash
# Quick install script for OKIN Bed BLE Controller
# Usage: curl -fsSL https://raw.githubusercontent.com/MaximumWorf/hassio-nectar/main/quick_install.sh | bash

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

# Get bed MAC address
echo "Enter the Bluetooth MAC address of your OKIN bed:"
echo "(Format: XX:XX:XX:XX:XX:XX)"
read -p "MAC Address: " BED_MAC

if [ -z "$BED_MAC" ]; then
    echo "ERROR: MAC address is required"
    exit 1
fi

# Get optional friendly name
read -p "Friendly name for this bed (default: 'OKIN Bed'): " BED_NAME
BED_NAME=${BED_NAME:-"OKIN Bed"}

# Install system dependencies
echo ""
echo "Installing system dependencies..."
sudo apt-get update -qq
sudo apt-get install -y python3 python3-pip python3-venv git bluez

# Clone or update repository
INSTALL_DIR="$HOME/okin-bed-control"
if [ -d "$INSTALL_DIR" ]; then
    echo ""
    echo "Updating existing installation..."
    cd "$INSTALL_DIR"
    git pull
else
    echo ""
    echo "Cloning repository..."
    git clone https://github.com/MaximumWorf/hassio-nectar.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# Install Python package with server dependencies
echo ""
echo "Installing Python package..."
cd okin_bed_control
pip3 install --user -e ".[server]"

# Create systemd service
echo ""
echo "Creating systemd service..."
SERVICE_FILE="/tmp/okin-bed-server.service"
cat > $SERVICE_FILE << EOF
[Unit]
Description=OKIN Bed BLE API Server - $BED_NAME
After=network.target bluetooth.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME
Environment="PATH=$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$HOME/.local/bin/okin-bed-server --mac $BED_MAC --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo cp $SERVICE_FILE /etc/systemd/system/okin-bed-server.service
sudo systemctl daemon-reload
sudo systemctl enable okin-bed-server.service

echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "Service: okin-bed-server"
echo "Bed: $BED_NAME"
echo "MAC: $BED_MAC"
echo "API URL: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "Commands:"
echo "  Start:   sudo systemctl start okin-bed-server"
echo "  Stop:    sudo systemctl stop okin-bed-server"
echo "  Status:  sudo systemctl status okin-bed-server"
echo "  Logs:    sudo journalctl -u okin-bed-server -f"
echo ""
echo "Next steps:"
echo "1. Start the service: sudo systemctl start okin-bed-server"
echo "2. Test: curl http://localhost:8000/health"
echo "3. Add to Home Assistant using the API URL above"
echo ""
