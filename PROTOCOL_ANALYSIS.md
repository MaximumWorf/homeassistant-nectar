# OKIN Adjustable Bed BLE Protocol Analysis

## Overview
This document contains the reverse-engineered Bluetooth Low Energy (BLE) protocol for the OKIN Adjustable Comfort - Luxe bed system, extracted from the Android app version 1.0.0.

## Application Details
- **Package Name**: `com.okin.bedding.luxe`
- **App Name**: Adjustable Comfort - Luxe
- **Version**: 1.0.0 (versionCode: 2)
- **BLE Framework**: Flutter Blue Plus

## BLE Service and Characteristic UUIDs

### Primary Service UUIDs
```
62741523-52F9-8864-B1AB-3B3A8D65950B  (OKIN Custom Service)
6E400001-B5A3-F393-E0A9-E50E24DCCA9E  (Nordic UART Service - NUS)
00001000-0000-1000-8000-00805f9b34fb  (Custom Service)
0000ffe0-0000-1000-8000-00805f9b34fb  (Custom Service)
```

### Characteristic UUIDs

#### OKIN Custom Characteristics
```
62741525-52F9-8864-B1AB-3B3A8D65950B  (TX - Write to device)
62741625-52F9-8864-B1AB-3B3A8D65950B  (RX - Read/Notify from device)
```

#### Nordic UART Service Characteristics
```
6E400002-B5A3-F393-E0A9-E50E24DCCA9E  (NUS TX - Write)
6E400003-B5A3-F393-E0A9-E50E24DCCA9E  (NUS RX - Read/Notify)
```

#### Other Characteristics
```
00001001-0000-1000-8000-00805f9b34fb
00001002-0000-1000-8000-00805f9b34fb
0000ffe9-0000-1000-8000-00805f9b34fb
0000ffe4-0000-1000-8000-00805f9b34fb
0000ffe5-0000-1000-8000-00805f9b34fb
00002902-0000-1000-8000-00805f9b34fb  (CCCD - Client Characteristic Configuration Descriptor)
```

## Supported Commands

Based on the decompiled app, the following commands are supported:

### Position Control
- **Head Up** - Raises the head section
- **Head Down** - Lowers the head section
- **Lumbar Up** - Raises the lumbar section
- **Lumbar Down** - Lowers the lumbar section
- **Foot Up** - Raises the foot section
- **Foot Down** - Lowers the foot section
- **Stop** - Stops all movement

### Preset Positions
- **Flat** - Returns bed to flat position
- **Zero Gravity** - Activates zero gravity position
- **Lounge** - Activates lounge position
- **Snore** (Anti-Snore) - Activates anti-snore position
- **Ascent** - Activates ascent position

### Massage Functions
- **Massage On** - Activates massage wave one
- **Massage Off** - Turns off massage motors
- **Wave One** - Massage wave pattern 1
- **Wave Two** - Massage wave pattern 2
- **Wave Three** - Massage wave pattern 3
- **Massage Intensity Control** - Adjust massage strength
  - Massage All Add (increase all)
  - Massage All Reduce (decrease all)
  - Massage Wave Add (increase wave intensity)
  - Massage Wave Reduce (decrease wave intensity)
  - Foot Strength Add
  - Foot Strength Reduce

### Lighting Control
- **Light On** - Activates under-bed lighting
- **Light Off** - Turns off under-bed lighting
- **Toggle Light** - Toggles light state
- **Increase Brightness** - Increases light brightness
- **Decrease Brightness** - Decreases light brightness

### Memory Functions
- **Memory Save** - Saves current position to memory
- **Memory Reset** - Resets memory position
- **Memory Recall** - Returns to saved position

## Protocol Details

### Communication Method
The bed uses BLE GATT (Generic Attribute Profile) for communication. Commands are sent by writing to specific characteristics, and responses/notifications are received via notify-enabled characteristics.

### Primary Communication Characteristics
Based on the UUID structure, the most likely communication path is:
- **Write Characteristic**: `62741525-52F9-8864-B1AB-3B3A8D65950B`
- **Read/Notify Characteristic**: `62741625-52F9-8864-B1AB-3B3A8D65950B`

Alternative path using Nordic UART Service:
- **Write Characteristic**: `6E400002-B5A3-F393-E0A9-E50E24DCCA9E`
- **Read/Notify Characteristic**: `6E400003-B5A3-F393-E0A9-E50E24DCCA9E`

### Command Structure
⚠️ **Note**: The exact byte-level command structure is not fully documented here as it requires:
1. Runtime BLE packet capture from the actual app
2. Analysis of the compiled Dart code in `libapp.so`
3. Live testing with the physical device

The commands are likely sent as byte arrays (Uint8List in Dart/Flutter) with a structure similar to:
```
[COMMAND_BYTE] [PARAMETER_1] [PARAMETER_2] ... [CHECKSUM?]
```

## Recommended Next Steps

To fully reverse-engineer the protocol:

1. **BLE Packet Capture**: Use Android tools like:
   - nRF Connect (Nordic Semiconductor)
   - BLE Scanner
   - Android HCI snoop log (Developer Options)

2. **Live Traffic Analysis**:
   - Enable Bluetooth HCI snoop logging on Android
   - Use the app to control the bed
   - Capture and analyze packets with Wireshark

3. **Pattern Analysis**:
   - Compare command sequences for different actions
   - Identify command structure, headers, checksums
   - Document parameter ranges for positions

## Security Considerations
- No obvious encryption or authentication observed in the BLE permissions
- The bed likely accepts commands from any connected BLE device
- Pairing may be required but likely no encryption

## Files Generated
- `PROTOCOL_ANALYSIS.md` - This file
- `okin_bed_control/` - Python project for Raspberry Pi
- `home_assistant/` - Home Assistant integration files

## References
- Flutter Blue Plus: https://pub.dev/packages/flutter_blue_plus
- Nordic UART Service: https://developer.nordicsemi.com/nRF_Connect_SDK/doc/latest/nrf/libraries/bluetooth_services/services/nus.html
- OKIN Website: https://www.okingroup.com/
