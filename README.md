# OKIN Adjustable Bed Control System

Complete reverse-engineered solution for controlling OKIN adjustable beds from Raspberry Pi with Home Assistant integration.

## 🎯 Project Overview

This project provides:
- ✅ Decompiled and analyzed OKIN bed Android app
- ✅ Documented BLE protocol (UUIDs and command list)
- ✅ Python library for Raspberry Pi
- ✅ Home Assistant custom integration
- ✅ Command-line interface
- ✅ **Captured and tested BLE command bytes** (Nectar Split King Luxe Adjustable Foundation)

## 📁 Project Structure

```
.
├── PROTOCOL_ANALYSIS.md          # BLE protocol documentation
├── CAPTURE_GUIDE.md               # Guide for capturing actual commands
├── REMOTE_SETUP.md                # Remote BLE setup guide
├── README.md                      # This file
│
├── extracted/                     # Extracted XAPK contents
├── decompiled/                    # Decompiled app source
│
├── okin_bed_control/              # Python library
│   ├── okin_bed/                  # Main package
│   │   ├── __init__.py
│   │   ├── bed.py                 # Main OkinBed class
│   │   ├── constants.py           # BLE UUIDs and commands
│   │   ├── scanner.py             # Device scanner
│   │   ├── cli.py                 # Command-line interface
│   │   └── api_server.py          # REST API server (remote mode)
│   ├── examples/
│   │   └── basic_control.py       # Usage examples
│   ├── setup.py
│   ├── install_server.sh          # API server installer
│   └── README.md
│
└── home_assistant/                # Home Assistant integration
    ├── custom_components/
    │   └── okin_bed/
    │       ├── __init__.py
    │       ├── manifest.json
    │       ├── const.py
    │       ├── config_flow.py     # UI configuration
    │       ├── coordinator.py     # Connection manager
    │       ├── cover.py           # Bed section controls
    │       ├── button.py          # Preset positions
    │       ├── switch.py          # Massage control
    │       └── light.py           # Under-bed lighting
    └── README.md
```

## 🔍 What Was Discovered

### BLE Service UUIDs
```
62741523-52F9-8864-B1AB-3B3A8D65950B  (OKIN Primary Service)
6E400001-B5A3-F393-E0A9-E50E24DCCA9E  (Nordic UART Service)
```

### BLE Characteristics
```
62741525-52F9-8864-B1AB-3B3A8D65950B  (TX - Write to bed)
62741625-52F9-8864-B1AB-3B3A8D65950B  (RX - Read from bed)
```

### Available Commands

**Position Control:**
- Head Up/Down
- Lumbar Up/Down
- Foot Up/Down
- Stop

**Preset Positions:**
- Flat
- Zero Gravity
- Lounge
- Anti-Snore (Snore)
- Ascent

**Massage:**
- Massage On/Off
- Wave 1, 2, 3
- Intensity controls

**Lighting:**
- Under-bed light on/off
- Brightness control
- Toggle

**Memory:**
- Save/Recall positions
- Reset memory

## 🚀 Quick Start

### 1. Install Python Library

```bash
cd okin_bed_control
pip install -e .
```

### 2. Find Your Bed

```bash
python -m okin_bed.scanner
```

Note the MAC address shown.

### 3. Test Basic Control

```python
from okin_bed import OkinBed
import asyncio

async def main():
    bed = OkinBed(mac_address="XX:XX:XX:XX:XX:XX")
    async with bed:
        await bed.zero_gravity()

asyncio.run(main())
```

### 4. Use CLI

```bash
okin-bed --mac XX:XX:XX:XX:XX:XX head-up
okin-bed --mac XX:XX:XX:XX:XX:XX zero-gravity
okin-bed --mac XX:XX:XX:XX:XX:XX massage-on
```

## ✅ Command Bytes Status

### **Captured and Tested!**

BLE command bytes have been **captured and verified** on a **Nectar Split King Luxe Adjustable Foundation**. All core functionality is working:

**Fully Tested Commands:**
- ✅ Position controls (Head, Lumbar, Foot - Up/Down/Stop)
- ✅ Presets (Flat, Zero Gravity, Anti-Snore, Lounge/TV)
- ✅ Massage (On/Off, Slow Pulse Wave)
- ✅ Under-bed lighting (On/Off)

**Not Yet Captured** (optional features):
- Ascent preset
- Additional massage wave patterns
- Light brightness controls

See `CAPTURED_COMMANDS.md` for the full capture and testing log.

### Testing on Other Bed Models

If you have a different OKIN bed model, the commands should work (they use a standard OKIN protocol), but some commands may vary. See **`CAPTURE_GUIDE.md`** if you need to capture commands for your specific model.

## 📱 Home Assistant Installation

### Method 1: HACS (Recommended) ⭐

1. **Add Custom Repository:**
   - HACS → Integrations → ⋮ (menu) → Custom repositories
   - Repository: `https://github.com/MaximumWorf/homeassistant-nectar`
   - Category: Integration
   - Click Add

2. **Install:**
   - HACS → Integrations → Search "OKIN"
   - Click "OKIN Adjustable Bed Control"
   - Click "Download"

3. **Restart Home Assistant**

4. **Configure:**
   - Settings → Devices & Services → Add Integration
   - Search "OKIN"
   - Follow setup wizard (choose Direct or Remote mode)

### Method 2: Manual Installation

```bash
cd /config  # or ~/.homeassistant
mkdir -p custom_components
cd custom_components
git clone https://github.com/MaximumWorf/homeassistant-nectar.git
cp -r homeassistant-nectar/okin_bed .
rm -rf homeassistant-nectar
```

Then restart and configure as above.

### Connection Modes

**Direct Mode** - HA device has Bluetooth
- Simplest setup
- HA connects directly to bed via BLE
- Choose this if your HA device is near the bed

**Remote Mode** - Separate BLE controller
- Dedicated Raspberry Pi near bed runs API server
- HA sends commands over network
- **Perfect for split king setups**
- See [Quick Install for BLE Controller](#ble-controller-quick-install) below

## 🔧 BLE Controller Installation (Remote Mode)

**Important:** ONE Raspberry Pi can control MULTIPLE beds! Perfect for split king setups. 🛏️+🛏️=1️⃣🥧

### Method 1: One-Liner Install (Easiest) ⭐

```bash
curl -fsSL https://raw.githubusercontent.com/MaximumWorf/homeassistant-nectar/main/quick_install.sh | bash
```

**For Split King:** Just run the same command twice!
- First run: Configure left bed (port 8000)
- Second run: Script detects existing install, adds right bed (port 8001)

This will:
- Install all dependencies (first run only)
- Set up API server(s) as systemd service(s)
- Configure autostart
- Each bed runs on its own port

### Method 2: Docker (Split King Ready)

```bash
# Clone repo
git clone https://github.com/MaximumWorf/homeassistant-nectar.git
cd homeassistant-nectar/okin_bed_control

# Edit docker-compose.yml
# - Set left bed MAC address (okin-bed-left service)
# - Uncomment and set right bed MAC address (okin-bed-right service)
nano docker-compose.yml

# Run both beds
docker-compose up -d
```

Docker will run TWO containers from ONE Raspberry Pi:
- Left bed: `http://RASPBERRY_PI_IP:8000`
- Right bed: `http://RASPBERRY_PI_IP:8001`

### Method 3: Manual Install

```bash
cd ~
git clone https://github.com/MaximumWorf/homeassistant-nectar.git
cd homeassistant-nectar/okin_bed_control
pip3 install -e ".[server]"
chmod +x install_server.sh
./install_server.sh  # Run once per bed
```

See `REMOTE_SETUP.md` for detailed remote setup guide.

## 🔧 Development

### Requirements
- Python 3.8+
- Raspberry Pi with Bluetooth LE (or any Linux with BLE)
- `bleak` library for BLE communication

### Running Tests
```bash
cd okin_bed_control
pip install -e ".[dev]"
pytest
```

### Contributing

Contributions welcome, especially:
1. **Protocol capture** - Most important!
2. Testing with different bed models
3. Additional features
4. Documentation improvements

## 📊 Protocol Analysis Details

See `PROTOCOL_ANALYSIS.md` for complete details on:
- BLE GATT structure
- Service and characteristic UUIDs
- Command mapping
- Security considerations

## 🛠️ Troubleshooting

### Can't find bed
- Ensure bed is powered on
- Check Bluetooth is enabled
- Try scanning with `bluetoothctl` or nRF Connect

### Connection fails
- Verify MAC address is correct
- Check bed isn't connected to phone app
- Try rebooting the bed (power cycle)

### Commands don't work
- Verify bed is powered on and connected
- Check that no other device (phone app) is connected
- Ensure you're using the correct MAC address
- If using a different bed model, commands may need to be re-captured (see `CAPTURE_GUIDE.md`)

## 📄 Files Documentation

| File | Purpose |
|------|---------|
| `PROTOCOL_ANALYSIS.md` | Complete BLE protocol documentation |
| `CAPTURE_GUIDE.md` | How to capture actual command bytes |
| `okin_bed_control/` | Python library for bed control |
| `home_assistant/` | Home Assistant integration |
| `decompiled/` | Decompiled app source code |
| `extracted/` | Extracted XAPK contents |

## 🔐 Security & Legal

### Security
- No encryption observed in BLE communication
- Bed accepts commands from any connected device
- Consider network isolation

### Legal & Disclaimer
- This is a reverse-engineered implementation
- Not affiliated with or endorsed by OKIN
- Use at your own risk
- For personal use and research only
- Test carefully to avoid damage or injury

## 📞 Support

- **Issues**: Open an issue on GitHub
- **Discussions**: Use GitHub Discussions
- **Protocol Help**: See `CAPTURE_GUIDE.md`

## 🎓 Learning Resources

- [Bleak Documentation](https://bleak.readthedocs.io/)
- [Bluetooth Low Energy Basics](https://learn.adafruit.com/introduction-to-bluetooth-low-energy)
- [Wireshark BLE Analysis](https://www.novelbits.io/bluetooth-sniffing-wireshark/)
- [Home Assistant Development](https://developers.home-assistant.io/)

## 📜 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

- Nordic Semiconductor for nRF Connect and BLE tools
- Flutter Blue Plus team
- Home Assistant community
- JADX decompiler project

---

**Next Step**: Follow `CAPTURE_GUIDE.md` to capture the actual BLE commands and complete this project!
