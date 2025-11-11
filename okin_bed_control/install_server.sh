#!/bin/bash
# Installation script for OKIN Bed API Server on Raspberry Pi

set -e

echo "========================================="
echo "OKIN Bed API Server Installation"
echo "========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Do not run this script as root"
    echo "Run as: ./install_server.sh"
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

# Install Python package with server dependencies
echo ""
echo "Installing okin-bed-control with server dependencies..."
pip3 install --user -e ".[server]"

# Create systemd service file
echo ""
echo "Creating systemd service..."
SERVICE_FILE="/tmp/okin-bed-server.service"
cat > $SERVICE_FILE << EOF
[Unit]
Description=OKIN Bed BLE API Server
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

# Install service
sudo cp $SERVICE_FILE /etc/systemd/system/okin-bed-server.service
sudo systemctl daemon-reload
sudo systemctl enable okin-bed-server.service

echo ""
echo "========================================="
echo "Installation complete!"
echo "========================================="
echo ""
echo "Service installed and enabled"
echo "Bed MAC Address: $BED_MAC"
echo "API will be available on: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "Commands:"
echo "  Start:   sudo systemctl start okin-bed-server"
echo "  Stop:    sudo systemctl stop okin-bed-server"
echo "  Status:  sudo systemctl status okin-bed-server"
echo "  Logs:    sudo journalctl -u okin-bed-server -f"
echo ""
echo "To start the server now, run:"
echo "  sudo systemctl start okin-bed-server"
echo ""
