"""BLE scanner for finding OKIN bed devices."""

import asyncio
import logging
from bleak import BleakScanner
from .constants import DEVICE_NAME_PATTERNS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def scan_for_beds(timeout: float = 10.0):
    """
    Scan for OKIN bed devices and display results.

    Args:
        timeout: Scan duration in seconds
    """
    logger.info(f"Scanning for BLE devices for {timeout} seconds...")
    logger.info(f"Looking for devices matching: {', '.join(DEVICE_NAME_PATTERNS)}")
    print()

    devices = await BleakScanner.discover(timeout=timeout)

    found_beds = []
    all_devices = []

    for device in devices:
        all_devices.append(device)
        if device.name:
            # Check if device matches OKIN patterns
            if any(pattern.lower() in device.name.lower() for pattern in DEVICE_NAME_PATTERNS):
                found_beds.append(device)

    # Display found OKIN beds
    if found_beds:
        print("=" * 70)
        print("FOUND OKIN BED DEVICES:")
        print("=" * 70)
        for device in found_beds:
            print(f"\nName:    {device.name}")
            print(f"Address: {device.address}")
            print(f"RSSI:    {device.rssi} dBm")
            if device.metadata:
                print(f"Metadata: {device.metadata}")
        print("=" * 70)
    else:
        print("No OKIN bed devices found.")
        print("\nShowing all discovered BLE devices:")
        print("=" * 70)
        for device in all_devices:
            name = device.name or "(Unknown)"
            print(f"{device.address:20} | {device.rssi:4} dBm | {name}")
        print("=" * 70)

    return found_beds


async def main():
    """Main scanner function."""
    import argparse

    parser = argparse.ArgumentParser(description="Scan for OKIN bed BLE devices")
    parser.add_argument(
        "--timeout",
        "-t",
        type=float,
        default=10.0,
        help="Scan duration in seconds (default: 10)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    await scan_for_beds(timeout=args.timeout)


if __name__ == "__main__":
    asyncio.run(main())
