#!/usr/bin/env python3
"""
Hold command script - sends command repeatedly like holding a button.

Usage:
    python3 hold_command.py <MAC> <command_hex> <duration>

Example:
    python3 hold_command.py XX:XX:XX:XX:XX:XX "5a 01 03 10 30 07 a5" 5
"""

import asyncio
import sys
from okin_bed import OkinBed


async def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    mac_address = sys.argv[1]
    command_hex = sys.argv[2]
    duration = float(sys.argv[3])

    # Parse hex command
    try:
        command_bytes = bytes([int(b, 16) for b in command_hex.split()])
    except ValueError as e:
        print(f"Error parsing hex command: {e}")
        sys.exit(1)

    print(f"Connecting to {mac_address}...")
    bed = OkinBed(mac_address=mac_address)

    try:
        if not await bed.connect():
            print("Failed to connect")
            return

        print(f"Holding command: {' '.join(f'{b:02x}' for b in command_bytes)}")
        print(f"Duration: {duration}s (sending every 0.1s)")

        # Send command repeatedly every 100ms (like holding a button)
        start_time = asyncio.get_event_loop().time()
        count = 0

        while (asyncio.get_event_loop().time() - start_time) < duration:
            await bed._send_command(command_bytes)
            count += 1
            await asyncio.sleep(0.1)

        print(f"Sent command {count} times")
        print("Sending STOP...")
        stop_cmd = bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x0f, 0xa5])
        await bed._send_command(stop_cmd)

        print("✓ Done")

    finally:
        try:
            await bed.disconnect()
        except:
            pass  # Ignore disconnect errors


if __name__ == '__main__':
    asyncio.run(main())
