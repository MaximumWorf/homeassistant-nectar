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

### 1.1 Quick Install (Recommended)

Single command installs everything:

```bash
curl -fsSL https://raw.githubusercontent.com/MaximumWorf/homeassistant-nectar/main/quick_install.sh | bash
```

The installer will:
- Install system dependencies (Python, Bluetooth, etc.)
- Clone repository and install Python package
- Create single systemd service (supports unlimited beds)
- Enable auto-start on boot
- Display your Pi's IP address and next steps

**No MAC address needed!** The v2.0.0 API server accepts all beds via query parameters.

### 1.2 Start the Server

```bash
# Start the service
sudo systemctl start okin-bed-server

# Check status
sudo systemctl status okin-bed-server

# View logs
sudo journalctl -u okin-bed-server -f
```

### 1.3 Find Server IP Address

```bash
# Get the IP address of this Pi
hostname -I
```

Note this IP address (e.g., `192.168.1.100`) - you'll need it for Home Assistant.

**Note:** The example IP `192.168.1.100` is a placeholder. Use your actual Pi's IP address shown by the command above.

### 1.4 Test API Server

```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response (before any beds connect):
# {"status":"healthy","total_beds":0,"connected_beds":0}

# Test a command (flat position) - requires MAC address as query parameter
curl -X POST "http://localhost:8000/preset/flat?mac=XX:XX:XX:XX:XX:XX"
# Replace XX:XX:XX:XX:XX:XX with your bed's MAC address
```

If the bed responds, the server is working correctly!

---

## Part 2: Home Assistant Setup

On your Home Assistant device (can be anywhere on the network).

### 2.1 Install Integration

```bash
# Copy integration to Home Assistant
cp -r ~/homeassistant-nectar/custom_components/okin_bed \
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

The BLE Controller Pi exposes these HTTP endpoints. **All command endpoints require a `mac` query parameter** to specify which bed to control.

### Position Controls (Continuous)
- `POST /head/up?mac=XX:XX:XX:XX:XX:XX` - Raise head (single increment)
- `POST /head/down?mac=XX:XX:XX:XX:XX:XX` - Lower head
- `POST /lumbar/up?mac=XX:XX:XX:XX:XX:XX` - Raise lumbar
- `POST /lumbar/down?mac=XX:XX:XX:XX:XX:XX` - Lower lumbar
- `POST /foot/up?mac=XX:XX:XX:XX:XX:XX` - Raise foot
- `POST /foot/down?mac=XX:XX:XX:XX:XX:XX` - Lower foot
- `POST /stop?mac=XX:XX:XX:XX:XX:XX` - Stop all movement

### Presets (One-Time)
- `POST /preset/flat?mac=XX:XX:XX:XX:XX:XX` - Flat position
- `POST /preset/zero-gravity?mac=XX:XX:XX:XX:XX:XX` - Zero gravity position
- `POST /preset/anti-snore?mac=XX:XX:XX:XX:XX:XX` - Anti-snore position
- `POST /preset/tv?mac=XX:XX:XX:XX:XX:XX` - TV viewing position
- `POST /preset/lounge?mac=XX:XX:XX:XX:XX:XX` - Lounge position

### Massage
- `POST /massage/on?mac=XX:XX:XX:XX:XX:XX` - Turn massage on
- `POST /massage/off?mac=XX:XX:XX:XX:XX:XX` - Turn massage off

### Lighting
- `POST /light/on?mac=XX:XX:XX:XX:XX:XX` - Turn under-bed light on
- `POST /light/off?mac=XX:XX:XX:XX:XX:XX` - Turn under-bed light off
- `POST /light/toggle?mac=XX:XX:XX:XX:XX:XX` - Toggle light

### System
- `GET /` - API information (shows all connected beds)
- `GET /health` - Health check (shows total beds and connected count)
- `POST /config` - Pre-configure bed MAC address (optional, beds auto-configure on first command)
- `POST /connect?mac=XX:XX:XX:XX:XX:XX` - Manually connect to specific bed
- `POST /disconnect?mac=XX:XX:XX:XX:XX:XX` - Disconnect from specific bed

---

## Multiple Beds (Split King)

**Great news!** ONE Raspberry Pi with ONE API server instance can control ALL beds! 🎉

### Single API Server, Multiple Beds (Recommended) ⭐

The API server now supports unlimited beds through a single instance. Each bed is identified by its MAC address in the API request.

**Setup:**
```bash
# Install the API server once (no MAC address needed)
cd ~/homeassistant-nectar/okin_bed_control
pip3 install --user -e ".[server]"
./install_server.sh
# Just press Enter when prompted for MAC (or provide one for pre-configuration)
```

The server runs on port 8000 and handles all beds dynamically.

**Home Assistant Configuration:**
1. Add first bed:
   - Connection mode: Remote (API server)
   - API URL: `http://192.168.1.100:8000`
   - MAC address: `XX:XX:XX:XX:XX:XX` (left bed MAC)
   - Name: "Left Bed"

2. Add second bed:
   - Connection mode: Remote (API server)
   - API URL: `http://192.168.1.100:8000` (same URL!)
   - MAC address: `YY:YY:YY:YY:YY:YY` (right bed MAC)
   - Name: "Right Bed"

**How it works:**
- Both beds use the same API URL (port 8000)
- Home Assistant automatically appends `?mac=XX:XX:XX:XX:XX:XX` to each request
- The server maintains separate BLE connections for each MAC address
- No need for multiple containers or ports!

**Benefits:**
- ✅ Single server instance for all beds
- ✅ No port configuration needed
- ✅ Add/remove beds without restarting server
- ✅ Unlimited bed support (within BLE range)
- ✅ Simpler deployment and maintenance

### Alternative: Docker Compose (Also Single Instance)

If using Docker:

```bash
# docker-compose.yml already configured for multi-bed support
cd ~/homeassistant-nectar/okin_bed_control
docker-compose up -d
```

Single container on port 8000 handles all beds. Same Home Assistant configuration as above.

### Legacy: Two BLE Controller Pis (For Large Rooms)

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
# Disconnect specific bed
curl -X POST "http://192.168.1.100:8000/disconnect?mac=XX:XX:XX:XX:XX:XX"

# Reconnect
curl -X POST "http://192.168.1.100:8000/connect?mac=XX:XX:XX:XX:XX:XX"
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
