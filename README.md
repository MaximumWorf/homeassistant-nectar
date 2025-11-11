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

### Connection Modes

This integration supports two connection modes:

**Direct Mode** (Default)
- Home Assistant device has Bluetooth
- HA connects directly to bed via BLE
- Simplest setup

**Remote Mode** (Recommended for split setups)
- Home Assistant on different device from BLE controller
- Dedicated Raspberry Pi near bed runs API server
- HA sends commands over network
- **See `REMOTE_SETUP.md` for detailed guide**

### Manual Installation
```bash
cp -r home_assistant/custom_components/okin_bed ~/.homeassistant/custom_components/
```

Then restart Home Assistant and add via Integrations:
1. Settings → Devices & Services → Add Integration
2. Search for "OKIN"
3. Select your bed
4. Choose connection mode (Direct or Remote)
5. If Remote: Enter API server URL (e.g., `http://192.168.1.100:8000`)
6. Name your bed

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
