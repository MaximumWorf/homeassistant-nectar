# Testing Guide for Captured Commands

Now that you have captured BLE commands, it's time to safely test them on your bed.

## Prerequisites

1. Make sure the bed is powered on
2. Know your bed's MAC address (from scanner)
3. **No one should be in the bed during testing**
4. Be ready to power off the bed if needed

## Find Your Bed's MAC Address

```bash
cd ~/nectar/hassio-nectar-main/okin_bed_control
python -m okin_bed.scanner
```

Note the MAC address (format: `XX:XX:XX:XX:XX:XX`)

## Option 1: Comprehensive Test Script (Recommended)

This script will walk you through testing all commands systematically:

```bash
cd ~/nectar/hassio-nectar-main/okin_bed_control
python3 examples/test_captured_commands.py XX:XX:XX:XX:XX:XX
```

**What it does:**
- Tests STOP command first (safety)
- Tests each position control for 0.5s with STOP after
- Tests preset positions
- Tests other commands (light, massage, etc.)
- Prompts you to describe what each command did
- Saves results to `test_results.txt`

**How to use:**
1. Run the script with your bed's MAC address
2. For each command, press ENTER to test it
3. Observe what the bed does
4. Type a description (e.g., "head up", "zero gravity", etc.)
5. Press 's' to skip a command, 'q' to quit

## Option 2: Quick Single Command Test

For testing individual commands quickly:

```bash
cd ~/nectar/hassio-nectar-main/okin_bed_control

# Test STOP (should do nothing)
python3 examples/quick_test.py XX:XX:XX:XX:XX:XX "5a 01 03 10 30 0f a5"

# Test Head Up? for 0.5 seconds
python3 examples/quick_test.py XX:XX:XX:XX:XX:XX "5a 01 03 10 30 01 a5" 0.5

# Test a preset (no duration needed)
python3 examples/quick_test.py XX:XX:XX:XX:XX:XX "5a 01 03 10 30 10 a5"
```

## Safety Protocol

### ALWAYS Test in This Order:

1. **First: Test STOP**
   ```bash
   python3 examples/quick_test.py XX:XX:XX:XX:XX:XX "5a 01 03 10 30 0f a5"
   ```
   This should do nothing. If it moves the bed, **STOP IMMEDIATELY**.

2. **Second: Test position controls briefly (0.5s)**
   - Start with small movements
   - Always send STOP after
   - Increase duration only if safe

3. **Third: Test presets**
   - These move to specific positions
   - May take several seconds
   - Watch the bed carefully

4. **Last: Test unknown commands**
   - Could be light, massage, or other features
   - Less risky than movement commands

### Emergency Stop

If anything goes wrong:
1. **Ctrl+C** to stop the script
2. **Power off the bed** at the wall/switch
3. Wait 10 seconds before powering back on

## Expected Commands

Based on the capture analysis:

### Position Controls (0.5s duration recommended)
```bash
# STOP (test first!)
5a 01 03 10 30 0f a5

# Likely movements
5a 01 03 10 30 01 a5  # HEAD_UP?
5a 01 03 10 30 00 a5  # HEAD_DOWN?
5a 01 03 10 30 07 a5  # FOOT_UP?
5a 01 03 10 30 02 a5  # FOOT_DOWN?
5a 01 03 10 30 03 a5  # LUMBAR_UP?
```

### Preset Positions (no duration)
```bash
5a 01 03 10 30 10 a5  # PRESET (flat/zero-g/lounge?)
5a 01 03 10 30 11 a5  # PRESET
5a 01 03 10 30 13 a5  # PRESET
5a 01 03 10 30 16 a5  # PRESET
```

### Other Functions (no duration)
```bash
5a 01 03 10 30 58 a5  # Light/Massage?
5a 01 03 10 30 6f a5  # Light/Massage?
5a 01 03 10 30 73 a5  # Light/Massage?
5a 01 03 10 30 74 a5  # Light/Massage?
```

## After Testing

### 1. Review Results

Check `test_results.txt` for your notes on what each command did.

### 2. Update constants.py

Edit `/root/nectar/okin_bed_control/okin_bed/constants.py`:

```python
class Command:
    # Position control
    HEAD_UP = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x01, 0xa5])  # Update with confirmed bytes
    HEAD_DOWN = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x00, 0xa5])
    FOOT_UP = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x07, 0xa5])
    # ... etc
```

### 3. Test the Library

Try using the updated library:

```python
from okin_bed import OkinBed
import asyncio

async def main():
    async with OkinBed(mac_address="XX:XX:XX:XX:XX:XX") as bed:
        print("Testing head up...")
        await bed.head_up()
        await asyncio.sleep(1)
        await bed.stop()

        print("Testing zero gravity preset...")
        await bed.zero_gravity()
        await asyncio.sleep(5)
        await bed.flat()

asyncio.run(main())
```

### 4. Commit Changes

```bash
git add okin_bed_control/okin_bed/constants.py
git add test_results.txt
git add CAPTURED_COMMANDS.md
git commit -m "Update with confirmed command bytes from testing"
git push
```

## Troubleshooting

### Bed doesn't respond
- Check Bluetooth connection
- Verify MAC address is correct
- Try power cycling the bed
- Disconnect the phone app if connected

### Commands do unexpected things
- **STOP TESTING IMMEDIATELY**
- Review the capture - you may have mixed up commands
- Try recapturing with one button at a time

### Connection drops
- Move closer to the bed
- Check for Bluetooth interference
- Restart Bluetooth on your system

## Tips

- **Keep a notebook** of what you test and what happens
- **Test systematically** - don't skip around
- **Be patient** - take breaks between tests
- **Document everything** - future you will thank you
- **When in doubt, STOP** - you can always test more later

## Need Help?

- Review `CAPTURED_COMMANDS.md` for command analysis
- Check `CAPTURE_GUIDE.md` for recapturing specific commands
- Open an issue on GitHub with your findings
