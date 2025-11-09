# OKIN Adjustable Bed Control

Python library for controlling OKIN adjustable beds via Bluetooth LE from a Raspberry Pi.

## Features

- Control bed positions (head, lumbar, foot)
- Activate preset positions (flat, zero gravity, lounge, anti-snore, ascent)
- Control massage functions (on/off, wave patterns, intensity)
- Control under-bed lighting
- Memory position management
- Home Assistant integration ready

## Requirements

- Python 3.8+
- Raspberry Pi with Bluetooth LE support (Pi 3, 4, Zero W, etc.)
- `bleak` library for BLE communication

## Installation

```bash
cd okin_bed_control
pip install -e .
```

## Quick Start

```python
from okin_bed import OkinBed
import asyncio

async def main():
    # Create bed controller
    bed = OkinBed()

    # Connect to the bed (auto-discover by name or use MAC address)
    await bed.connect()

    # Control the bed
    await bed.head_up()
    await asyncio.sleep(2)
    await bed.stop()

    # Use preset positions
    await bed.zero_gravity()

    # Control massage
    await bed.massage_on()
    await bed.set_massage_wave(2)

    # Disconnect
    await bed.disconnect()

asyncio.run(main())
```

## Configuration

### Finding Your Bed's MAC Address

```bash
# Run the scanner
python -m okin_bed.scanner

# Or use bluetoothctl
sudo bluetoothctl
scan on
# Look for devices with "OKIN" or "Adjustable" in the name
```

### Environment Variables

Create a `.env` file:

```
OKIN_BED_MAC=XX:XX:XX:XX:XX:XX
OKIN_BED_NAME=Adjustable Comfort
```

## Command Line Interface

```bash
# Basic commands
okin-bed head-up
okin-bed head-down
okin-bed foot-up
okin-bed foot-down
okin-bed stop

# Presets
okin-bed flat
okin-bed zero-gravity
okin-bed lounge

# Massage
okin-bed massage-on
okin-bed massage-off
okin-bed massage-wave 2

# Lighting
okin-bed light-on
okin-bed light-off
okin-bed light-brightness 50
```

## API Documentation

See `docs/API.md` for complete API documentation.

## Home Assistant Integration

See `../home_assistant/` directory for Home Assistant custom component.

## Protocol Research

This library is based on reverse engineering the OKIN Android app. The BLE protocol details are documented in `../PROTOCOL_ANALYSIS.md`.

⚠️ **Important**: This is a reverse-engineered implementation. Use at your own risk. Always test commands carefully and ensure safety.

## Contributing

Contributions welcome! Especially:
- Protocol refinements from packet captures
- Testing with different OKIN bed models
- Additional features

## License

MIT License - See LICENSE file

## Disclaimer

This project is not affiliated with or endorsed by OKIN. Use at your own risk.
