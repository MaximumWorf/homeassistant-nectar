"""Basic example of controlling an OKIN bed."""

import asyncio
import logging
from okin_bed import OkinBed

logging.basicConfig(level=logging.INFO)


async def main():
    """Main example function."""
    # Create bed controller
    # You can specify MAC address or let it auto-discover
    bed = OkinBed(
        # mac_address="XX:XX:XX:XX:XX:XX",  # Optional
        # device_name="Adjustable Comfort",  # Optional
    )

    try:
        # Connect using async context manager
        async with bed:
            print("Connected to bed!")

            # Raise head for 2 seconds
            print("Raising head...")
            await bed.head_up()
            await asyncio.sleep(2)
            await bed.stop()

            await asyncio.sleep(1)

            # Go to zero gravity position
            print("Moving to zero gravity position...")
            await bed.zero_gravity()
            await asyncio.sleep(5)

            # Turn on massage
            print("Turning on massage...")
            await bed.massage_on()
            await asyncio.sleep(10)

            # Change to wave 2
            print("Switching to wave 2...")
            await bed.set_massage_wave(2)
            await asyncio.sleep(10)

            # Turn off massage
            print("Turning off massage...")
            await bed.massage_off()
            await asyncio.sleep(2)

            # Return to flat
            print("Returning to flat position...")
            await bed.flat()
            await asyncio.sleep(5)

            print("Demo complete!")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
