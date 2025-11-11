# Remote BLE Setup Guide

This guide explains how to set up OKIN bed control when **Home Assistant and the bed are on different devices**.

## Architecture Overview

```
┌─────────────────────┐         HTTP/Network        ┌──────────────────────┐
│  Home Assistant Pi  │ ◄────────────────────────── │   BLE Controller Pi  │
│  (No Bluetooth)     │                             │  (Near Bed)          │
│                     │         REST API            │                      │
│  • HA Integration   │                             │  • API Server        │
│  • Sends Commands   │                             │  • BLE Connection    │
└─────────────────────┘                             └──────────────────────┘
                                                              │
                                                              │ Bluetooth LE
                                                              ▼
                                                      ┌──────────────┐
                                                      │  OKIN Bed    │
                                                      │              │
                                                      └──────────────┘
```

**Why use this setup?**
- Your Home Assistant server doesn't have Bluetooth
- Your Home Assistant is too far from the bed for reliable BLE
- You want a dedicated Raspberry Pi near the bed for BLE control

## Setup Overview

1. **BLE Controller Pi** (near bed): Runs API server with Bluetooth connection
2. **Home Assistant Pi** (anywhere): Sends HTTP commands to API server

---

## Part 1: BLE Controller Pi Setup

This Raspberry Pi must be **close to the bed** (within Bluetooth range).

### 1.1 Install Python Library

```bash
# Clone repository
cd ~
git clone https://github.com/MaximumWorf/homeassistant-nectar.git
cd homeassistant-nectar/okin_bed_control

# Install with server dependencies
pip3 install --user -e ".[server]"
```

### 1.2 Configure and Install Service

```bash
# Make installation script executable
chmod +x install_server.sh

# Run installer (will prompt for bed MAC address)
./install_server.sh
```

The installer will:
- Install the Python package with server dependencies (FastAPI, uvicorn)
- Prompt you for your bed's Bluetooth MAC address
- Create and enable systemd service
- Configure autostart on boot

### 1.3 Start the Server

```bash
# Start the service
sudo systemctl start okin-bed-server

# Check status
sudo systemctl status okin-bed-server

# View logs
sudo journalctl -u okin-bed-server -f
```

### 1.4 Find Server IP Address

```bash
# Get the IP address of this Pi
hostname -I
```

Note this IP address (e.g., `192.168.1.100`) - you'll need it for Home Assistant.

### 1.5 Test API Server

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","bed_connected":true}

# Test a command (flat position)
curl -X POST http://localhost:8000/preset/flat
```

If the bed responds, the server is working correctly!

---

## Part 2: Home Assistant Setup

On your Home Assistant device (can be anywhere on the network).

### 2.1 Install Integration

```bash
# Copy integration to Home Assistant
cp -r ~/homeassistant-nectar/home_assistant/custom_components/okin_bed \
  /config/custom_components/

# Restart Home Assistant
# Settings → System → Restart
```

### 2.2 Add Integration via UI

1. **Settings → Devices & Services → Add Integration**
2. Search for **"OKIN"**
3. **Select your bed** from discovered devices (this step still uses Bluetooth discovery for pairing info)
4. **Choose connection mode: "Remote (API server on another device)"**
5. **Enter API Server URL**: `http://192.168.1.100:8000` (use your BLE Pi's IP)
6. **Name your bed**: e.g., "Master Bed", "Left Bed", "Right Bed"
7. Click **Submit**

### 2.3 Verify Connection

Check Home Assistant logs for connection confirmation:

```
INFO Connected to remote OKIN bed API: http://192.168.1.100:8000
```

---

## API Endpoints Reference

The BLE Controller Pi exposes these HTTP endpoints:

### Position Controls (Continuous)
- `POST /head/up` - Raise head (single increment)
- `POST /head/down` - Lower head
- `POST /lumbar/up` - Raise lumbar
- `POST /lumbar/down` - Lower lumbar
- `POST /foot/up` - Raise foot
- `POST /foot/down` - Lower foot
- `POST /stop` - Stop all movement

### Presets (One-Time)
- `POST /preset/flat` - Flat position
- `POST /preset/zero-gravity` - Zero gravity position
- `POST /preset/anti-snore` - Anti-snore position
- `POST /preset/tv` - TV viewing position
- `POST /preset/lounge` - Lounge position

### Massage
- `POST /massage/on` - Turn massage on
- `POST /massage/off` - Turn massage off

### Lighting
- `POST /light/on` - Turn under-bed light on
- `POST /light/off` - Turn under-bed light off
- `POST /light/toggle` - Toggle light

### System
- `GET /` - API information
- `GET /health` - Health check
- `POST /config` - Configure bed MAC address

---

## Multiple Beds (Split King)

**Good news!** ONE Raspberry Pi can control BOTH beds in a split king setup! 🎉

### Option 1: One BLE Controller Pi (Recommended) ⭐

Single Pi running two API server instances on different ports - **super easy now!**

**Setup:**
```bash
# Run the installer once for each bed
curl -fsSL https://raw.githubusercontent.com/MaximumWorf/homeassistant-nectar/main/quick_install.sh | bash
# Enter left bed MAC, port 8000

curl -fsSL https://raw.githubusercontent.com/MaximumWorf/homeassistant-nectar/main/quick_install.sh | bash
# Script detects existing install, prompts for right bed MAC, port 8001
```

The script automatically:
- Detects existing installations
- Creates separate systemd services (`okin-bed-server-1`, `okin-bed-server-2`)
- Configures different ports (8000, 8001)
- Shows all configured beds

**Home Assistant Configuration:**
1. Add first bed: Remote mode → `http://192.168.1.100:8000` → Name: "Left Bed"
2. Add second bed: Remote mode → `http://192.168.1.100:8001` → Name: "Right Bed"

**Benefits:**
- ✅ Single device to manage
- ✅ Lower cost (one Pi instead of two)
- ✅ Simpler network setup
- ✅ Works great if both beds are within BLE range (~30 feet)

### Option 2: Two BLE Controller Pis (For Large Rooms)

Only needed if beds are far apart (>30 feet) or in different rooms.

- One Pi per bed (each runs on port 8000)
- Different IP addresses for each Pi

**Home Assistant Configuration:**
1. Add first bed: Remote mode → `http://192.168.1.100:8000` → Name: "Left Bed"
2. Add second bed: Remote mode → `http://192.168.1.101:8000` → Name: "Right Bed"

---

## Troubleshooting

### API Server Won't Start

```bash
# Check logs
sudo journalctl -u okin-bed-server -n 50

# Common issues:
# - Wrong MAC address in service file
# - Python package not installed
# - Port 8000 already in use
```

**Fix service configuration:**
```bash
# Edit service file
sudo nano /etc/systemd/system/okin-bed-server.service

# Update MAC address on ExecStart line
# Save and restart
sudo systemctl daemon-reload
sudo systemctl restart okin-bed-server
```

### Home Assistant Can't Connect to API

**Test from HA host:**
```bash
# Can you reach the server?
ping 192.168.1.100

# Can you access the API?
curl http://192.168.1.100:8000/health
```

**Common issues:**
- Firewall blocking port 8000 on BLE Pi
- Wrong IP address
- API server not running

**Open firewall (if needed):**
```bash
# On BLE Controller Pi
sudo ufw allow 8000/tcp
```

### Bed Commands Not Working

**Check API server logs:**
```bash
sudo journalctl -u okin-bed-server -f
```

Watch logs while sending commands from Home Assistant.

**Common issues:**
- Bed not powered on
- Bed MAC address incorrect
- BLE connection lost (bed too far from Pi)

**Reconnect manually:**
```bash
curl -X POST http://192.168.1.100:8000/disconnect
curl -X POST http://192.168.1.100:8000/connect
```

### Connection Reliability

**Enable API server logging:**
Edit `/etc/systemd/system/okin-bed-server.service`:
```ini
Environment="PYTHONUNBUFFERED=1"
```

Then reload and restart:
```bash
sudo systemctl daemon-reload
sudo systemctl restart okin-bed-server
```

---

## Advanced Configuration

### Change API Port

Edit service file:
```bash
sudo nano /etc/systemd/system/okin-bed-server.service
```

Change `--port 8000` to desired port, then:
```bash
sudo systemctl daemon-reload
sudo systemctl restart okin-bed-server
```

### Auto-Reconnect on BLE Disconnect

The API server automatically reconnects on each command. No additional configuration needed.

### Secure the API (Optional)

The API has no authentication by default (designed for local network only).

**Firewall restriction (recommended):**
```bash
# Only allow Home Assistant IP
sudo ufw allow from 192.168.1.50 to any port 8000 proto tcp
sudo ufw deny 8000/tcp
sudo ufw enable
```

Replace `192.168.1.50` with your Home Assistant IP.

---

## Performance Notes

- **Latency**: Expect ~50-200ms for commands (network + BLE)
- **Continuous movements**: Commands sent every 500ms for press-and-hold
- **Connection**: API maintains persistent BLE connection to bed
- **Reliability**: Auto-reconnects if BLE connection drops

---

## Comparison: Direct vs Remote Mode

| Feature | Direct Mode | Remote Mode |
|---------|-------------|-------------|
| **Requirements** | HA has Bluetooth | Separate BLE Pi |
| **Setup Complexity** | Simple | Moderate |
| **Range** | HA must be near bed | BLE Pi can be anywhere near bed |
| **Latency** | ~50ms | ~100-200ms |
| **Multiple Beds** | Limited by BLE range | Easy with multiple Pis |
| **Reliability** | Depends on HA Bluetooth | Dedicated BLE connection |

---

## Summary

**BLE Controller Pi:**
```bash
cd ~/homeassistant-nectar/okin_bed_control
pip3 install --user -e ".[server]"
./install_server.sh
sudo systemctl start okin-bed-server
hostname -I  # Note the IP
```

**Home Assistant:**
1. Install integration
2. Add Integration → OKIN Bed
3. Choose "Remote" mode
4. Enter `http://BLE_PI_IP:8000`
5. Name your bed

Done! All entities will now send commands via the remote API.
