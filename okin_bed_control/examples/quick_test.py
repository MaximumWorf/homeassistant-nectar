#!/usr/bin/env python3
"""
Quick test script - send a single command to the bed.

Usage:
    python3 quick_test.py <MAC> <command_hex>

Examples:
    # Test STOP
    python3 quick_test.py XX:XX:XX:XX:XX:XX "5a 01 03 10 30 0f a5"

    # Test Head Up for 0.5s
    python3 quick_test.py XX:XX:XX:XX:XX:XX "5a 01 03 10 30 01 a5" 0.5

    # Test a preset (no duration)
    python3 quick_test.py XX:XX:XX:XX:XX:XX "5a 01 03 10 30 10 a5"
"""

import asyncio
import sys
from okin_bed import OkinBed


async def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    mac_address = sys.argv[1]
    command_hex = sys.argv[2]
    duration = float(sys.argv[3]) if len(sys.argv) > 3 else 0

    # Parse hex command
    try:
        command_bytes = bytes([int(b, 16) for b in command_hex.split()])
    except ValueError as e:
        print(f"Error parsing hex command: {e}")
        print("Format: '5a 01 03 10 30 0f a5' (space-separated hex bytes)")
        sys.exit(1)

    print(f"Connecting to {mac_address}...")
    bed = OkinBed(mac_address=mac_address)

    try:
        if not await bed.connect():
            print("Failed to connect")
            return

        print(f"Sending command: {' '.join(f'{b:02x}' for b in command_bytes)}")
        await bed._send_command(command_bytes)

        if duration > 0:
            print(f"Running for {duration}s...")
            await asyncio.sleep(duration)
            print("Sending STOP...")
            stop_cmd = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x0f, 0xa5])
            await bed._send_command(stop_cmd)

        print("✓ Done")

    finally:
        await bed.disconnect()


if __name__ == '__main__':
    asyncio.run(main())
