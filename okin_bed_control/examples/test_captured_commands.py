#!/usr/bin/env python3
"""
Test script for captured OKIN bed commands.

SAFETY WARNINGS:
- Do NOT test with anyone in the bed
- Be ready to power off the bed if needed
- Test commands are SHORT duration (0.5s)
- You can abort at any time with Ctrl+C
"""

import asyncio
import sys
from okin_bed import OkinBed

# Captured commands from btsnoop_hci_202511091908.cfa
COMMANDS = {
    'STOP': bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x0f, 0xa5]),

    # Position controls (held button patterns)
    'CMD_01_HEAD_UP?': bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x01, 0xa5]),
    'CMD_00_HEAD_DOWN?': bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x00, 0xa5]),
    'CMD_07_FOOT_UP?': bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x07, 0xa5]),
    'CMD_02_FOOT_DOWN?': bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x02, 0xa5]),
    'CMD_03_LUMBAR_UP?': bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x03, 0xa5]),

    # Preset positions (few uses)
    'PRESET_10': bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x10, 0xa5]),
    'PRESET_11': bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x11, 0xa5]),
    'PRESET_13': bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x13, 0xa5]),
    'PRESET_16': bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x16, 0xa5]),

    # Unknown (possibly light/massage)
    'CMD_58': bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x58, 0xa5]),
    'CMD_6F': bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x6f, 0xa5]),
    'CMD_73': bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x73, 0xa5]),
    'CMD_74': bytes([0x5a, 0x01, 0x03, 0x10, 0x30, 0x74, 0xa5]),

    # Special command
    'SPECIAL_B0': bytes([0x5a, 0xb0, 0x00, 0xa5]),
}


async def test_command(bed, name, command_bytes, duration=0.5):
    """
    Test a single command.

    Args:
        bed: OkinBed instance
        name: Command name
        command_bytes: Bytes to send
        duration: How long to run command (seconds)
    """
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"Bytes:   {' '.join(f'{b:02x}' for b in command_bytes)}")
    print(f"Duration: {duration}s")
    print(f"{'='*70}")

    response = input("Press ENTER to test this command (or 's' to skip, 'q' to quit): ").strip().lower()

    if response == 'q':
        print("\nQuitting test sequence.")
        return False
    elif response == 's':
        print("Skipped.")
        return True

    try:
        print(f"Sending command...")
        await bed._send_command(command_bytes)

        if duration > 0:
            await asyncio.sleep(duration)
            print(f"Sending STOP...")
            await bed._send_command(COMMANDS['STOP'])

        print("\n✓ Command sent successfully")

        result = input("What happened? (describe or press ENTER): ").strip()
        if result:
            print(f"Recorded: {result}")
            with open('/root/nectar/test_results.txt', 'a') as f:
                f.write(f"{name}: {result}\n")

        # Wait a bit before next command
        await asyncio.sleep(1)
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


async def main():
    """Main test sequence."""

    if len(sys.argv) < 2:
        print("Usage: python3 test_captured_commands.py <MAC_ADDRESS>")
        print("Example: python3 test_captured_commands.py XX:XX:XX:XX:XX:XX")
        sys.exit(1)

    mac_address = sys.argv[1]

    print("=" * 70)
    print("OKIN BED COMMAND TEST SCRIPT")
    print("=" * 70)
    print("\n⚠️  SAFETY WARNINGS:")
    print("  - Do NOT test with anyone in the bed")
    print("  - Be ready to power off the bed if needed")
    print("  - Each command will run for 0.5 seconds then STOP")
    print("  - You can skip or quit at any time")
    print("  - Results will be saved to test_results.txt")
    print("\n" + "=" * 70)

    response = input("\nAre you ready to begin testing? (yes/no): ").strip().lower()
    if response != 'yes':
        print("Test cancelled.")
        return

    print(f"\nConnecting to bed at {mac_address}...")

    bed = OkinBed(mac_address=mac_address)

    try:
        connected = await bed.connect()
        if not connected:
            print("Failed to connect to bed. Exiting.")
            return

        print("✓ Connected successfully\n")

        # Step 1: Test STOP command first
        print("\n" + "=" * 70)
        print("STEP 1: Testing STOP command")
        print("This is the most important command - it should do nothing.")
        print("=" * 70)

        await test_command(bed, 'STOP', COMMANDS['STOP'], duration=0)

        print("\n\nDid the STOP command work correctly (did nothing)?")
        response = input("Continue with movement tests? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Test cancelled.")
            return

        # Step 2: Test position controls
        print("\n" + "=" * 70)
        print("STEP 2: Testing Position Controls")
        print("These should move bed sections briefly (0.5s)")
        print("=" * 70)

        position_commands = [
            'CMD_01_HEAD_UP?',
            'CMD_00_HEAD_DOWN?',
            'CMD_07_FOOT_UP?',
            'CMD_02_FOOT_DOWN?',
            'CMD_03_LUMBAR_UP?',
        ]

        for cmd_name in position_commands:
            if not await test_command(bed, cmd_name, COMMANDS[cmd_name], duration=0.5):
                break

        # Step 3: Test presets
        print("\n" + "=" * 70)
        print("STEP 3: Testing Preset Positions")
        print("These might move bed to preset positions")
        print("=" * 70)

        response = input("Continue with preset tests? (yes/no): ").strip().lower()
        if response == 'yes':
            preset_commands = [
                'PRESET_10',
                'PRESET_11',
                'PRESET_13',
                'PRESET_16',
            ]

            for cmd_name in preset_commands:
                if not await test_command(bed, cmd_name, COMMANDS[cmd_name], duration=0):
                    break

        # Step 4: Test other commands
        print("\n" + "=" * 70)
        print("STEP 4: Testing Other Commands")
        print("These might be light, massage, or other features")
        print("=" * 70)

        response = input("Continue with other command tests? (yes/no): ").strip().lower()
        if response == 'yes':
            other_commands = [
                'CMD_58',
                'CMD_6F',
                'CMD_73',
                'CMD_74',
                'SPECIAL_B0',
            ]

            for cmd_name in other_commands:
                if not await test_command(bed, cmd_name, COMMANDS[cmd_name], duration=0):
                    break

        print("\n" + "=" * 70)
        print("Testing Complete!")
        print("=" * 70)
        print("\nResults have been saved to test_results.txt")
        print("Review the results and update okin_bed_control/okin_bed/constants.py")

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\n\nError during testing: {e}")
    finally:
        print("\nDisconnecting...")
        await bed.disconnect()
        print("Disconnected.")


if __name__ == '__main__':
    asyncio.run(main())
