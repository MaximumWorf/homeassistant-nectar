"""The OKIN Adjustable Bed integration."""

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_MAC_ADDRESS,
    CONF_DEVICE_NAME,
    CONF_CONNECTION_MODE,
    CONF_API_URL,
    MODE_DIRECT,
)
from .coordinator import OkinBedCoordinator

_LOGGER = logging.getLogger(__name__)

# Version check for debugging
_LOGGER.warning("OKIN Bed Integration Loading - Version 2.0.3")

PLATFORMS: list[Platform] = [
    Platform.COVER,
    Platform.BUTTON,
    Platform.SWITCH,
    Platform.LIGHT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up OKIN Bed from a config entry."""
    _LOGGER.info("Setting up OKIN Bed integration for %s", entry.data.get(CONF_DEVICE_NAME))
    hass.data.setdefault(DOMAIN, {})

    # Get connection mode and API URL (if set)
    connection_mode = entry.data.get(CONF_CONNECTION_MODE, MODE_DIRECT)
    api_url = entry.data.get(CONF_API_URL)

    # Create coordinator for this bed
    coordinator = OkinBedCoordinator(
        hass,
        entry.data[CONF_MAC_ADDRESS],
        entry.data[CONF_DEVICE_NAME],
        connection_mode,
        api_url,
    )

    # Store coordinator
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up all platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Disconnect from bed and cleanup
        coordinator: OkinBedCoordinator = hass.data[DOMAIN][entry.entry_id]
        await coordinator.async_disconnect()

        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
