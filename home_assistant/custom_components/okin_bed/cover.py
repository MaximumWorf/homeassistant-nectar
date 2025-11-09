"""Support for OKIN Bed covers (bed sections)."""

import logging
from typing import Any

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_MAC_ADDRESS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OKIN Bed cover entities."""
    mac_address = config_entry.data[CONF_MAC_ADDRESS]

    entities = [
        OkinBedSection(mac_address, "head", "Head"),
        OkinBedSection(mac_address, "lumbar", "Lumbar"),
        OkinBedSection(mac_address, "foot", "Foot"),
    ]

    async_add_entities(entities)


class OkinBedSection(CoverEntity):
    """Representation of an OKIN bed section as a cover."""

    _attr_device_class = CoverDeviceClass.AWNING
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
    )

    def __init__(self, mac_address: str, section: str, name: str) -> None:
        """Initialize the bed section cover."""
        self._mac_address = mac_address
        self._section = section
        self._attr_name = f"OKIN Bed {name}"
        self._attr_unique_id = f"{mac_address}_{section}"
        self._is_opening = False
        self._is_closing = False

    @property
    def is_opening(self) -> bool:
        """Return if the cover is opening."""
        return self._is_opening

    @property
    def is_closing(self) -> bool:
        """Return if the cover is closing."""
        return self._is_closing

    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed."""
        # Position tracking would require feedback from the bed
        return None

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover (raise section)."""
        _LOGGER.info(f"Opening {self._section} section")
        self._is_opening = True
        self._is_closing = False

        # TODO: Implement actual BLE command
        # For now this is a placeholder
        # await self._send_command(f"{self._section}_up")

        self.async_write_ha_state()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover (lower section)."""
        _LOGGER.info(f"Closing {self._section} section")
        self._is_closing = True
        self._is_opening = False

        # TODO: Implement actual BLE command
        # await self._send_command(f"{self._section}_down")

        self.async_write_ha_state()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        _LOGGER.info(f"Stopping {self._section} section")
        self._is_opening = False
        self._is_closing = False

        # TODO: Implement actual BLE command
        # await self._send_command("stop")

        self.async_write_ha_state()
