# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a reverse-engineered Bluetooth Low Energy (BLE) control system for OKIN adjustable beds. The project provides:
- Python library (`okin_bed_control/`) for Raspberry Pi control
- Home Assistant custom integration (`home_assistant/`)
- Decompiled Android app analysis (`decompiled/`, `extracted/`)
- Protocol documentation

**Critical Status**: The BLE command bytes in `okin_bed_control/okin_bed/constants.py` are **placeholder values**. The actual byte sequences must be captured from real BLE traffic using the official app (see CAPTURE_GUIDE.md).

## Project Architecture

### Python Library Structure

The core library follows a clean async/await pattern using the `bleak` library:

1. **OkinBed class** (`okin_bed_control/okin_bed/bed.py`):
   - Main controller implementing all bed functions
   - Handles BLE connection lifecycle via `bleak.BleakClient`
   - Auto-discovers characteristics (OKIN custom service or Nordic UART Service)
   - All control methods are async coroutines
   - Implements async context manager (`async with bed:`)

2. **Constants** (`okin_bed_control/okin_bed/constants.py`):
   - BLE UUIDs (confirmed from decompiled app):
     - OKIN Service: `62741523-52F9-8864-B1AB-3B3A8D65950B`
     - TX Characteristic: `62741525-52F9-8864-B1AB-3B3A8D65950B`
     - RX Characteristic: `62741625-52F9-8864-B1AB-3B3A8D65950B`
   - Command byte placeholders in `Command` class
   - Enums for positions, massage waves, light states

3. **Scanner** (`okin_bed_control/okin_bed/scanner.py`):
   - BLE device discovery using `BleakScanner`
   - Matches device names against patterns (OKIN, Adjustable, Comfort, Luxe)

4. **CLI** (`okin_bed_control/okin_bed/cli.py`):
   - Command-line interface using argparse
   - Entry point: `okin-bed` command

### Home Assistant Integration

Located in `home_assistant/custom_components/okin_bed/`:

- **Platform Support**: Cover, Switch, Light, Sensor entities
- **Config Flow**: UI-based configuration (config_flow: true in manifest.json)
- **Bluetooth Integration**: Uses HA's bluetooth integration (declared in manifest.json)
- **Structure**:
  - `__init__.py`: Entry point, platform setup
  - `cover.py`: Bed section controls (head, lumbar, foot)
  - `const.py`: Integration constants
  - `manifest.json`: Integration metadata

### Decompiled App Analysis

The `decompiled/` and `extracted/` directories contain reverse-engineered Android app code:
- App uses Flutter with `flutter_blue_plus` for BLE
- Provides confirmed UUIDs and command list
- Voice command files in `assets/md/` show full feature set

## Development Commands

### Python Library Development

```bash
# Install in development mode
cd okin_bed_control
pip install -e .

# Install with dev dependencies (when implemented)
pip install -e ".[dev]"

# Run tests (when implemented)
pytest

# Scan for bed devices
python -m okin_bed.scanner

# Use CLI
okin-bed --mac XX:XX:XX:XX:XX:XX head-up
```

### Home Assistant Testing

```bash
# Copy integration to HA custom_components
cp -r home_assistant/custom_components/okin_bed ~/.homeassistant/custom_components/

# Restart Home Assistant
systemctl restart home-assistant@homeassistant
# or via HA UI: Settings -> System -> Restart
```

### BLE Protocol Capture

The **most critical development task** is capturing actual command bytes:

```bash
# Android: Enable Bluetooth HCI snoop log
# Settings -> Developer Options -> Bluetooth HCI snoop log -> ON

# Pull captured log
adb pull /sdcard/btsnoop_hci.log

# Analyze with Wireshark
wireshark btsnoop_hci.log

# Filter for writes to OKIN TX characteristic
# Filter: bluetooth.uuid == 0x62741525
```

See CAPTURE_GUIDE.md for detailed instructions.

## Key Code Patterns

### Async BLE Communication

All bed control methods are async and follow this pattern:

```python
async def control_method(self):
    """Method docstring."""
    await self._send_command(Command.SOME_COMMAND)
```

The `_send_command()` method:
- Checks connection status
- Validates TX characteristic exists
- Writes to BLE characteristic via `client.write_gatt_char()`
- Adds delay between commands (COMMAND_DELAY)

### Connection Management

Two patterns are supported:

```python
# Pattern 1: Explicit connect/disconnect
bed = OkinBed(mac_address="XX:XX:XX:XX:XX:XX")
await bed.connect()
await bed.head_up()
await bed.disconnect()

# Pattern 2: Context manager (preferred)
async with OkinBed(mac_address="XX:XX:XX:XX:XX:XX") as bed:
    await bed.head_up()
```

### Characteristic Discovery

The library tries to find characteristics in order:
1. OKIN custom service (62741523-...)
2. Nordic UART Service (6E400001-...)
3. Fallback: First writable/notifiable characteristics

This is handled in `_discover_characteristics()` method.

## Important Implementation Notes

### Command Byte Updates

When actual command bytes are captured:

1. Update `okin_bed_control/okin_bed/constants.py`
2. Replace placeholder `bytes([0xXX])` with actual captured sequences
3. Commands may have structure like: `[HEADER] [COMMAND] [PARAM1] [PARAM2] [CHECKSUM]`
4. Test each command individually before committing

### Safety Considerations

- Never test commands with someone in the bed
- Always implement a stop/emergency mechanism
- Test with low-risk commands first (flat, stop)
- Power cycling the bed is the ultimate safety measure

### BLE Connection Quirks

- Bed may only accept one connection at a time (disconnect phone app first)
- Connection timeout is 30 seconds (CONNECTION_TIMEOUT)
- Some beds may disconnect after period of inactivity
- Characteristics may vary between bed models (hence fallback discovery)

## Testing Strategy

### Protocol Capture Testing

Create test scripts in `okin_bed_control/examples/`:

```python
# test_captured_commands.py
async def test_command(bed, name, command_bytes):
    print(f"Testing: {name}")
    print(f"Bytes: {command_bytes.hex()}")
    await bed._send_command(command_bytes)
    await asyncio.sleep(2)
    input("Press Enter if worked, Ctrl+C to abort...")
```

### Integration Testing

For Home Assistant:
- Test each platform (cover, switch, light)
- Verify entity state updates
- Test automations
- Check logs for BLE errors

## File Locations

### Primary Development Files
- `okin_bed_control/okin_bed/bed.py` - Main controller class
- `okin_bed_control/okin_bed/constants.py` - **UPDATE THIS with captured command bytes**
- `home_assistant/custom_components/okin_bed/cover.py` - HA cover entities

### Documentation
- `PROTOCOL_ANALYSIS.md` - Confirmed BLE protocol details
- `CAPTURE_GUIDE.md` - Step-by-step capture instructions
- `QUICK_REFERENCE.md` - Quick lookup reference
- `README.md` - Project overview

### Reference Material
- `decompiled/` - Decompiled Android app source
- `extracted/` - Extracted XAPK contents

## Dependencies

### Python Library
- `bleak>=0.20.0` - BLE communication (cross-platform)
- `asyncio` - Async/await support (standard library)

### Home Assistant
- Home Assistant Core 2023.1+ (for bluetooth integration support)
- `bleak` via HA's bluetooth integration

### Development Tools
- `adb` - Android Debug Bridge (for BLE capture)
- `wireshark` - BLE packet analysis
- nRF Connect app (alternative capture method)

## Git Workflow

This repository is configured with:
- User: MaximumWorf
- Email: chad.veloso@gmail.com
- Remote: https://github.com/MaximumWorf/hassio-nectar.git
- Branch: main

## Legal and Security

- **Not affiliated with OKIN** - This is reverse-engineered
- **No encryption** observed in BLE protocol
- **Open access** - Bed accepts commands from any connected device
- **Use at own risk** - Thoroughly test before regular use
- **Personal/research use only** - Not for commercial distribution
