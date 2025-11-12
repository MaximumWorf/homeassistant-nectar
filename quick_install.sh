#!/bin/bash
# Quick install script for OKIN Bed BLE Controller
# Single-instance API server with multi-bed support via MAC query parameters
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

INSTALL_DIR="$HOME/okin-bed-control"
SERVICE_NAME="okin-bed-server"

# Check for existing installation
if systemctl list-units --full --all | grep -q "$SERVICE_NAME.service"; then
    echo "✓ OKIN Bed API Server is already installed"
    echo ""
    sudo systemctl status $SERVICE_NAME --no-pager || true
    echo ""
    read -p "Update installation and restart service? (y/n): " UPDATE </dev/tty
    if [[ ! "$UPDATE" =~ ^[Yy]$ ]]; then
        echo "Installation cancelled"
        exit 0
    fi
    UPDATING=true
else
    echo "Installing OKIN Bed API Server (v2.0.0)"
    echo "Single instance supports unlimited beds!"
    echo ""
    UPDATING=false
fi

# Install system dependencies
if [ "$UPDATING" = false ]; then
    echo "Installing system dependencies..."
    sudo apt-get update -qq
    sudo apt-get install -y python3 python3-pip python3-venv git bluez
fi

# Clone or update repository
if [ -d "$INSTALL_DIR" ]; then
    echo ""
    echo "Updating repository..."
    cd "$INSTALL_DIR"
    git pull
else
    echo ""
    echo "Cloning repository..."
    git clone https://github.com/MaximumWorf/homeassistant-nectar.git "$INSTALL_DIR"
fi

# Install Python package with server dependencies
echo ""
echo "Installing Python package..."
cd "$INSTALL_DIR/okin_bed_control"
pip3 install --user -e ".[server]"

# Create single systemd service
echo ""
echo "Creating systemd service..."
SERVICE_FILE="/tmp/${SERVICE_NAME}.service"
cat > $SERVICE_FILE << 'EOF'
[Unit]
Description=OKIN Bed BLE API Server (Multi-Bed)
After=network.target bluetooth.target

[Service]
Type=simple
User=USER_PLACEHOLDER
WorkingDirectory=HOME_PLACEHOLDER
Environment="PATH=HOME_PLACEHOLDER/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=HOME_PLACEHOLDER/.local/bin/okin-bed-server --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Replace placeholders
sed -i "s|USER_PLACEHOLDER|$USER|g" $SERVICE_FILE
sed -i "s|HOME_PLACEHOLDER|$HOME|g" $SERVICE_FILE

sudo cp $SERVICE_FILE /etc/systemd/system/${SERVICE_NAME}.service
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}.service

if [ "$UPDATING" = true ]; then
    echo ""
    echo "Restarting service..."
    sudo systemctl restart ${SERVICE_NAME}.service
fi

echo ""
echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo ""
echo "Service: $SERVICE_NAME"
echo "API Port: 8000"
echo "API URL: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "This single server instance can control unlimited beds!"
echo "Each bed is identified by its MAC address in API requests."
echo ""
echo "Commands:"
echo "  Start:   sudo systemctl start $SERVICE_NAME"
echo "  Stop:    sudo systemctl stop $SERVICE_NAME"
echo "  Status:  sudo systemctl status $SERVICE_NAME"
echo "  Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo ""
echo "Next steps:"
echo "1. Start the service: sudo systemctl start $SERVICE_NAME"
echo "2. Test: curl http://localhost:8000/health"
echo "   Expected: {\"status\":\"healthy\",\"total_beds\":0,\"connected_beds\":0}"
echo ""
echo "3. Add to Home Assistant:"
echo "   - Settings → Devices & Services → Add Integration"
echo "   - Search for 'OKIN'"
echo "   - Choose 'Remote (API server on another device)'"
echo "   - API URL: http://$(hostname -I | awk '{print $1}'):8000"
echo "   - Enter your bed's MAC address"
echo "   - Repeat for additional beds (same API URL, different MAC)"
echo ""
echo "For split king setups:"
echo "  - Left Bed:  Same API URL, MAC: XX:XX:XX:XX:XX:XX"
echo "  - Right Bed: Same API URL, MAC: YY:YY:YY:YY:YY:YY"
echo ""
