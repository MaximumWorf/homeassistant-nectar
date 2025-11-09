"""Command-line interface for OKIN bed control."""

import asyncio
import argparse
import logging
import sys
from typing import Optional

from .bed import OkinBed
from .constants import BedPosition, MassageWave

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def execute_command(
    bed: OkinBed,
    command: str,
    args: argparse.Namespace
) -> bool:
    """
    Execute a bed control command.

    Args:
        bed: OkinBed instance
        command: Command to execute
        args: Command-line arguments

    Returns:
        True if command executed successfully, False otherwise
    """
    try:
        # Position control commands
        if command == "head-up":
            await bed.head_up()
        elif command == "head-down":
            await bed.head_down()
        elif command == "lumbar-up":
            await bed.lumbar_up()
        elif command == "lumbar-down":
            await bed.lumbar_down()
        elif command == "foot-up":
            await bed.foot_up()
        elif command == "foot-down":
            await bed.foot_down()
        elif command == "stop":
            await bed.stop()

        # Preset positions
        elif command == "flat":
            await bed.flat()
        elif command == "zero-gravity":
            await bed.zero_gravity()
        elif command == "lounge":
            await bed.lounge()
        elif command == "anti-snore":
            await bed.anti_snore()
        elif command == "ascent":
            await bed.ascent()

        # Massage control
        elif command == "massage-on":
            await bed.massage_on()
        elif command == "massage-off":
            await bed.massage_off()
        elif command == "massage-wave":
            if not args.wave:
                logger.error("Wave number required (1, 2, or 3)")
                return False
            await bed.set_massage_wave(args.wave)

        # Lighting control
        elif command == "light-on":
            await bed.light_on()
        elif command == "light-off":
            await bed.light_off()
        elif command == "light-toggle":
            await bed.light_toggle()
        elif command == "brightness-up":
            await bed.brightness_up()
        elif command == "brightness-down":
            await bed.brightness_down()

        else:
            logger.error(f"Unknown command: {command}")
            return False

        logger.info(f"Command '{command}' executed successfully")
        return True

    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return False


async def async_main(args: argparse.Namespace) -> int:
    """
    Async main function.

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Create bed controller
    bed = OkinBed(
        mac_address=args.mac_address,
        device_name=args.device_name
    )

    try:
        # Connect to bed
        logger.info("Connecting to bed...")
        if not await bed.connect(timeout=args.timeout):
            logger.error("Failed to connect to bed")
            return 1

        # Execute command
        success = await execute_command(bed, args.command, args)

        # Disconnect
        await bed.disconnect()

        return 0 if success else 1

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        await bed.disconnect()
        return 130

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await bed.disconnect()
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Control OKIN adjustable bed via Bluetooth LE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  okin-bed head-up
  okin-bed zero-gravity
  okin-bed massage-wave 2
  okin-bed --mac XX:XX:XX:XX:XX:XX flat
        """
    )

    parser.add_argument(
        "command",
        help="Command to execute",
        choices=[
            "head-up", "head-down", "lumbar-up", "lumbar-down",
            "foot-up", "foot-down", "stop",
            "flat", "zero-gravity", "lounge", "anti-snore", "ascent",
            "massage-on", "massage-off", "massage-wave",
            "light-on", "light-off", "light-toggle",
            "brightness-up", "brightness-down"
        ]
    )

    parser.add_argument(
        "--mac-address", "-m",
        help="Bluetooth MAC address of the bed"
    )

    parser.add_argument(
        "--device-name", "-n",
        help="Bluetooth device name"
    )

    parser.add_argument(
        "--wave", "-w",
        type=int,
        choices=[1, 2, 3],
        help="Massage wave number (1, 2, or 3)"
    )

    parser.add_argument(
        "--timeout", "-t",
        type=float,
        default=30.0,
        help="Connection timeout in seconds (default: 30)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run async main
    exit_code = asyncio.run(async_main(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
