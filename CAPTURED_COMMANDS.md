# Captured OKIN Bed BLE Commands

**Capture Date:** 2025-11-09
**Capture File:** btsnoop_hci_202511091908.cfa
**BLE Handle:** 0x0016 (TX Characteristic)

## Summary

Successfully captured **15 unique command sequences** from the OKIN bed Android app.

## Command Structure

Most commands follow this pattern:
```
5a 01 03 10 30 XX a5
```

Where:
- `5a` = Start byte / Header
- `01 03 10` = Command header
- `30` = Section identifier (0x30 = main control)
- `XX` = Action byte (varies by command)
- `a5` = Checksum / End byte

## Captured Commands (TESTED & CONFIRMED)

| # | Hex Bytes                    | Action Byte | Pattern | **CONFIRMED Function** |
|---|------------------------------|-------------|---------|------------------------|
| 1 | `5a 01 03 10 30 00 a5`       | `00`        | Held    | **HEAD UP** ✓ |
| 2 | `5a 01 03 10 30 0f a5`       | `0f`        | Single  | **STOP** ✓ |
| 3 | `5a 01 03 10 30 01 a5`       | `01`        | Held    | **HEAD DOWN** ✓ |
| 4 | `5a 01 03 10 30 07 a5`       | `07`        | Held    | **LUMBAR DOWN** ✓ |
| 5 | `5a 01 03 10 30 02 a5`       | `02`        | Held    | **FOOT UP** ✓ |
| 6 | `5a 01 03 10 30 03 a5`       | `03`        | Held    | **FOOT DOWN** ✓ |
| 7 | `5a 01 03 10 30 10 a5`       | `10`        | Few     | **FLAT** ✓ |
| 8 | `5a 01 03 10 30 13 a5`       | `13`        | Few     | **ZERO GRAVITY** ✓ |
| 9 | `5a 01 03 10 30 11 a5`       | `11`        | Few     | **TV/LOUNGE MODE** ✓ |
| 10 | `5a 01 03 10 30 16 a5`       | `16`        | Few     | **ANTI-SNORE** ✓ |
| 11 | `5a b0 00 a5`                | N/A         | Single  | Unknown (not tested) |
| 12 | `5a 01 03 10 30 58 a5`       | `58`        | Single  | **MASSAGE ON** ✓ |
| 13 | `5a 01 03 10 30 6f a5`       | `6f`        | Single  | Does nothing |
| 14 | `5a 01 03 10 30 73 a5`       | `73`        | Single  | **LIGHT ON** ✓ |
| 15 | `5a 01 03 10 30 74 a5`       | `74`        | Single  | **LIGHT OFF** ✓ |

## Additional Discovered Commands

**LUMBAR UP** - Found via systematic testing: `5a 01 03 10 30 04 a5` ✓

## Command Byte Pattern

Position controls follow a logical pattern:
```
00 = HEAD_UP
01 = HEAD_DOWN
02 = FOOT_UP
03 = FOOT_DOWN
04 = LUMBAR_UP ✓ (discovered via testing)
07 = LUMBAR_DOWN
0f = STOP
```

## Still Missing Commands

May need additional BLE capture:
- **MASSAGE OFF** - Likely requires separate button press capture
- **MASSAGE WAVE patterns** - If bed supports multiple massage modes
- **LIGHT BRIGHTNESS controls** - If bed supports dimming

## Timing Analysis

### Rapid-Fire Commands (Held Buttons)
Commands that appear in rapid succession (~100ms apart) are position controls:
- Around 128-129s: 9 commands in 1s (button held)
- Around 135-136s: 9 commands in 1s (button held)
- Around 152-153s: 13 commands in 1s (button held)
- Around 166-168s: 17 commands in 2s (button held longer)

### Single/Few Commands (Presets)
Commands that appear once or 2-3 times are likely preset positions:
- Around 179s: 2 commands (preset activation?)
- Around 184s: 2 commands (preset activation?)
- Around 208s: 2 commands (preset activation?)

### Stop Command Pattern
The `0x0f` byte appears consistently between command sequences, suggesting it's the STOP command sent when button is released.

## Next Steps

### To Complete the Mapping:

1. **Review what you did in the app** at these timestamps:
   - What was happening around 128s, 135s, 152s, etc.?
   - Did you press Head Up, Foot Up, or other controls?

2. **Do a controlled capture**:
   - Clear the log
   - Press ONE button at a time
   - Note which button you pressed
   - Pull the log
   - Match the command to the button

3. **Test the commands safely**:
   ```python
   async with OkinBed(mac_address="YOUR_MAC") as bed:
       # Test stop first
       await bed._send_command(bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x0f, 0xa5]))
       await asyncio.sleep(1)

       # Test a position command (be ready to stop!)
       await bed._send_command(bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x01, 0xa5]))
       await asyncio.sleep(0.5)
       await bed._send_command(bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x0f, 0xa5]))
   ```

## Proposed Command Mapping

Based on patterns and protocol analysis:

```python
class Command:
    # Position control
    HEAD_UP = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x01, 0xa5])
    HEAD_DOWN = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x00, 0xa5])
    FOOT_UP = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x07, 0xa5])
    FOOT_DOWN = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x02, 0xa5])
    LUMBAR_UP = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x03, 0xa5])
    LUMBAR_DOWN = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x??, 0xa5])  # Not captured
    STOP = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x0f, 0xa5])

    # Presets (need to confirm which is which)
    PRESET_1 = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x10, 0xa5])
    PRESET_2 = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x11, 0xa5])
    PRESET_3 = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x13, 0xa5])
    PRESET_4 = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x16, 0xa5])

    # Special
    SPECIAL = bytes([0x5a, 0xb0, 0x00, 0xa5])  # Unknown purpose
```

## Safety Notes

- **ALWAYS test STOP command first** before testing any movement commands
- **Never test with someone in the bed**
- **Be ready to power off the bed** if something goes wrong
- **Test each command for short duration** (0.5s max) initially
- **Verify the bed responds correctly** before using longer durations

## Files to Update

Once commands are confirmed:
1. `okin_bed_control/okin_bed/constants.py` - Update Command class
2. Test with `okin_bed_control/examples/test_commands.py`
3. Update this document with confirmed mappings
4. Commit and push to repository
