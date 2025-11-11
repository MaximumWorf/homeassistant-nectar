# OKIN Bed Control - Quick Reference

## BLE UUIDs (Confirmed)

### Services
```
OKIN Primary:    62741523-52F9-8864-B1AB-3B3A8D65950B
Nordic UART:     6E400001-B5A3-F393-E0A9-E50E24DCCA9E
```

### Characteristics (OKIN)
```
TX (Write):      62741525-52F9-8864-B1AB-3B3A8D65950B
RX (Read/Notify):62741625-52F9-8864-B1AB-3B3A8D65950B
```

### Characteristics (Nordic UART Service)
```
TX (Write):      6E400002-B5A3-F393-E0A9-E50E24DCCA9E
RX (Read/Notify):6E400003-B5A3-F393-E0A9-E50E24DCCA9E
```

## Command List (From App)

### Basic Controls
| Command | Action |
|---------|--------|
| Head Up | Raise head section |
| Head Down | Lower head section |
| Lumbar Up | Raise lumbar section |
| Lumbar Down | Lower lumbar section |
| Foot Up | Raise foot section |
| Foot Down | Lower foot section |
| Stop | Stop all movement |

### Presets
| Command | Action |
|---------|--------|
| Flat | Return to flat |
| Zero Gravity | Zero-G position |
| Lounge | Lounge position |
| Snore (Anti-Snore) | Anti-snore position |
| Ascent | Ascent position |

### Massage
| Command | Action |
|---------|--------|
| Massage On | Start massage (wave 1) |
| Massage Off | Stop massage |
| Wave One | Massage pattern 1 |
| Wave Two | Massage pattern 2 |
| Wave Three | Massage pattern 3 |

### Lighting
| Command | Action |
|---------|--------|
| Light On | Turn under-bed light on |
| Light Off | Turn under-bed light off |
| Toggle Light | Toggle light state |
| Increase Brightness | Increase brightness |
| Decrease Brightness | Decrease brightness |

## Python Library Usage

### Install
```bash
cd okin_bed_control
pip install -e .
```

### Basic Example
```python
from okin_bed import OkinBed
import asyncio

async def main():
    bed = OkinBed(mac_address="XX:XX:XX:XX:XX:XX")

    async with bed:
        await bed.head_up()
        await asyncio.sleep(2)
        await bed.stop()

        await bed.zero_gravity()
        await bed.massage_on()

asyncio.run(main())
```

### CLI Commands
```bash
# Find bed
python -m okin_bed.scanner

# Control bed
okin-bed --mac XX:XX:XX:XX:XX:XX head-up
okin-bed --mac XX:XX:XX:XX:XX:XX zero-gravity
okin-bed --mac XX:XX:XX:XX:XX:XX massage-wave 2
okin-bed --mac XX:XX:XX:XX:XX:XX flat
```

## Packet Capture

### Enable Android HCI Snoop
```
Settings → Developer Options → Bluetooth HCI snoop log → ON
```

### Pull Log
```bash
adb pull /sdcard/btsnoop_hci.log
```

### Analyze with Wireshark
```bash
wireshark btsnoop_hci.log
```

### Filter
```
bluetooth.uuid == 0x62741525
```

## Testing Procedure

1. **Scan for bed**:
   ```bash
   python -m okin_bed.scanner
   ```

2. **Note MAC address**

3. **Test connection**:
   ```python
   bed = OkinBed(mac_address="XX:XX:XX:XX:XX:XX")
   await bed.connect()
   print(f"Connected: {bed._connected}")
   await bed.disconnect()
   ```

4. **Capture commands** (see CAPTURE_GUIDE.md)

5. **Update constants.py** with real command bytes

6. **Test each command** carefully

## Home Assistant Quick Setup

### Install
```bash
cp -r home_assistant/custom_components/okin_bed \
    ~/.homeassistant/custom_components/
```

### Restart HA
```bash
systemctl restart home-assistant@homeassistant
```

### Add Integration
```
Settings → Devices & Services → Add Integration → OKIN Bed
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't find bed | Check bed is on, Bluetooth enabled |
| Connection fails | Power cycle bed, check MAC address |
| Commands don't work | Verify bed powered, no other device connected |
| Permission denied | Add user to `bluetooth` group |

## Important Notes

✅ **Command bytes tested** - Captured and verified on Nectar Split King Luxe

⚠️ **Test safely** - Don't test with someone in bed

⚠️ **Not official** - Reverse engineered, use at own risk

⚠️ **Other bed models** - Commands may vary, see CAPTURE_GUIDE.md

## Key Files

| File | Purpose |
|------|---------|
| `PROTOCOL_ANALYSIS.md` | Full protocol documentation |
| `CAPTURE_GUIDE.md` | How to capture commands |
| `README.md` | Main documentation |
| `okin_bed/constants.py` | UUIDs and command bytes |
| `okin_bed/bed.py` | Main control class |

## Next Steps

1. ✅ Decompile app - DONE
2. ✅ Find UUIDs - DONE
3. ✅ Create Python library - DONE
4. ✅ Create HA integration - DONE
5. ⏳ **Capture real command bytes** - TODO
6. ⏳ Test and refine - TODO

**Current Task**: Follow `CAPTURE_GUIDE.md` to capture the actual BLE commands!
