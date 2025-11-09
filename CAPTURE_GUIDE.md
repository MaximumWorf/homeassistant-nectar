# BLE Protocol Capture Guide

This guide explains how to capture and analyze the actual Bluetooth Low Energy commands used by the OKIN bed app.

## Why This is Needed

The decompiled app shows:
- ✅ BLE service and characteristic UUIDs
- ✅ Available commands (head up, massage on, etc.)
- ✅ Flutter Blue Plus is used for BLE communication

What we still need:
- ❌ Actual byte sequences for each command
- ❌ Command structure (headers, parameters, checksums)
- ❌ Response/acknowledgment format

## Method 1: Android HCI Snoop Log (Recommended)

### Setup

1. **Enable Developer Options** on your Android device:
   - Go to Settings → About Phone
   - Tap "Build Number" 7 times

2. **Enable Bluetooth HCI Snoop Log**:
   - Go to Settings → Developer Options
   - Find "Bluetooth HCI snoop log"
   - Enable it

3. **Install the OKIN App**:
   - Install the `Adjustable Comfort - Luxe_1.0.0_APKPure.xapk` file
   - You may need to extract and install via ADB

### Capture Process

1. **Clear old logs**:
   ```bash
   adb shell
   rm /sdcard/btsnoop_hci.log
   exit
   ```

2. **Restart Bluetooth**:
   - Turn Bluetooth OFF and ON on your phone
   - This starts a fresh capture

3. **Use the app**:
   - Open the OKIN app
   - Connect to your bed
   - Perform ONE action at a time (e.g., "Head Up")
   - Wait 2-3 seconds
   - Perform next action
   - Repeat for all commands you want to capture

4. **Pull the log file**:
   ```bash
   adb pull /sdcard/btsnoop_hci.log
   ```

### Analysis with Wireshark

1. **Open in Wireshark**:
   ```bash
   wireshark btsnoop_hci.log
   ```

2. **Filter for BLE writes**:
   ```
   bluetooth.uuid == 0x62741525 || bluetooth.uuid == 0x6e400002
   ```

3. **Analyze patterns**:
   - Look for `ATT Write Request` or `ATT Write Command` packets
   - Compare byte values for different commands
   - Document the patterns

### Example Wireshark Output

You'll see packets like:
```
ATT Write Request, Handle: 0x001c (62741525-52F9-8864-B1AB-3B3A8D65950B)
    Value: 01 10 00 3c
```

This tells you:
- Handle: The characteristic being written to
- Value: The actual command bytes (this is what we need!)

## Method 2: Using nRF Connect (Simple GUI Method)

### Setup

1. Install **nRF Connect** on your Android phone
2. Install the OKIN app as well

### Capture Process

1. **Scan and find the bed**:
   - Open nRF Connect
   - Scan for devices
   - Find your OKIN bed
   - Connect to it

2. **Find the characteristics**:
   - Look for service `62741523-...`
   - Note the TX characteristic `62741525-...`
   - Note the RX characteristic `62741625-...`

3. **Enable notifications** on RX characteristic

4. **Use the OKIN app**:
   - Switch to OKIN app
   - Send a command (e.g., Head Up)
   - Quickly switch back to nRF Connect

5. **Check the log**:
   - nRF Connect logs all writes and notifications
   - Document the byte values for each command

## Method 3: BLE Sniffer Hardware (Advanced)

### Required Hardware
- nRF52840 Dongle or similar BLE sniffer
- Wireshark with nRF Sniffer plugin

### Setup
1. Flash the nRF Sniffer firmware to the dongle
2. Install Wireshark and nRF Sniffer extcap plugin
3. Configure Wireshark to use the sniffer

### Advantages
- Captures all traffic without needing device access
- No phone modifications needed
- Can see both directions of communication

### Disadvantages
- Requires additional hardware
- More complex setup
- May miss packets due to channel hopping

## Analyzing the Captured Data

### What to Look For

1. **Command Structure**:
   ```
   [HEADER] [COMMAND] [PARAMETER_1] [PARAMETER_2] ... [CHECKSUM?]
   ```

2. **Common Patterns**:
   - Fixed header bytes that appear in all commands
   - Command identifier (different for each action)
   - Parameters (position values, intensity, etc.)
   - Checksum or CRC at the end

3. **Command Mapping**:
   Create a table like this:

   | Command | Bytes (Hex) | Notes |
   |---------|-------------|-------|
   | Head Up | `01 10 00 3c` | 3c might be duration |
   | Head Down | `01 11 00 3c` | Notice 11 vs 10 |
   | Stop | `01 00 00 00` | All zeros after header |
   | Flat | `02 00 00 00` | Different header? |
   | Zero Gravity | `02 01 00 00` | Preset positions |
   | Massage On Wave 1 | `03 01 01 00` | 01 = wave number? |
   | Massage On Wave 2 | `03 01 02 00` | 02 = wave number? |

### Updating the Code

Once you have the command bytes, update `/root/nectar/okin_bed_control/okin_bed/constants.py`:

```python
class Command:
    # Position control (replace with actual values)
    HEAD_UP = bytes([0x01, 0x10, 0x00, 0x3c])
    HEAD_DOWN = bytes([0x01, 0x11, 0x00, 0x3c])
    # ... etc
```

## Testing Your Findings

### Safety First
⚠️ **IMPORTANT**: Test carefully!
- Start with simple commands (stop, flat)
- Don't test while someone is in the bed
- Be ready to power off the bed if needed

### Test Script

Create a test script:

```python
import asyncio
from okin_bed import OkinBed

async def test_command(bed, name, command_bytes):
    print(f"Testing: {name}")
    print(f"Bytes: {command_bytes.hex()}")
    await bed._send_command(command_bytes)
    await asyncio.sleep(2)
    input("Press Enter if this worked, Ctrl+C to abort...")

async def main():
    bed = OkinBed(mac_address="XX:XX:XX:XX:XX:XX")
    await bed.connect()

    try:
        # Test commands one by one
        await test_command(bed, "Head Up", bytes([0x01, 0x10, 0x00, 0x3c]))
        await test_command(bed, "Head Down", bytes([0x01, 0x11, 0x00, 0x3c]))
        # etc...
    finally:
        await bed.disconnect()

asyncio.run(main())
```

## Alternative: Packet Capture on Raspberry Pi

If you're already using a Raspberry Pi:

1. **Install btmon**:
   ```bash
   sudo apt-get install bluez
   ```

2. **Start monitoring**:
   ```bash
   sudo btmon | tee ble_capture.log
   ```

3. **In another terminal, run your test script**:
   ```bash
   python test_commands.py
   ```

4. **Stop btmon** (Ctrl+C) and analyze the log

## Resources

- **Wireshark BLE Tutorial**: https://www.novelbits.io/bluetooth-sniffing-wireshark/
- **nRF Connect**: https://www.nordicsemi.com/Products/Development-tools/nrf-connect-for-mobile
- **nRF Sniffer**: https://www.nordicsemi.com/Products/Development-tools/nRF-Sniffer-for-Bluetooth-LE
- **BLE Packet Analysis**: https://learn.adafruit.com/reverse-engineering-a-bluetooth-low-energy-light-bulb

## Contributing

Once you've captured the protocol:

1. Update the constants in the Python library
2. Test thoroughly
3. Document your findings
4. Submit a pull request or create an issue with your findings

## Need Help?

If you successfully capture the protocol or need help:
- Open an issue on GitHub
- Include sample packet captures (sanitized of personal data)
- Describe what you've found and what's unclear
