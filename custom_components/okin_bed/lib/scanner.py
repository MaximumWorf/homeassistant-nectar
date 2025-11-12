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

    # Dictionary to store devices with their advertisement data
    devices_found = {}

    def detection_callback(device, advertisement_data):
        """Callback for each discovered device."""
        devices_found[device.address] = {
            'device': device,
            'rssi': advertisement_data.rssi,
            'name': device.name or advertisement_data.local_name or "(Unknown)"
        }

    # Scan with callback to get RSSI
    scanner = BleakScanner(detection_callback=detection_callback)
    await scanner.start()
    await asyncio.sleep(timeout)
    await scanner.stop()

    found_beds = []
    all_devices = []

    for addr, data in devices_found.items():
        device = data['device']
        name = data['name']
        rssi = data['rssi']

        all_devices.append(data)

        # Check if device matches OKIN patterns
        if name and any(pattern.lower() in name.lower() for pattern in DEVICE_NAME_PATTERNS):
            found_beds.append(data)

    # Display found OKIN beds
    if found_beds:
        print("=" * 70)
        print("FOUND OKIN BED DEVICES:")
        print("=" * 70)
        for data in found_beds:
            device = data['device']
            print(f"\nName:    {data['name']}")
            print(f"Address: {device.address}")
            print(f"RSSI:    {data['rssi']} dBm")
        print("=" * 70)
    else:
        print("No OKIN bed devices found.")
        print("\nShowing all discovered BLE devices:")
        print("=" * 70)
        for data in sorted(all_devices, key=lambda x: x['rssi'], reverse=True):
            device = data['device']
            name = data['name']
            rssi = data['rssi']
            print(f"{device.address:20} | {rssi:4} dBm | {name}")
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
