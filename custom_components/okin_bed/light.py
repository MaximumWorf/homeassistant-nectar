"""Support for OKIN Bed lights (under-bed lighting)."""

import logging
from typing import Any

from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_DEVICE_NAME
from .coordinator import OkinBedCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OKIN Bed light entities."""
    coordinator: OkinBedCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    device_name = config_entry.data[CONF_DEVICE_NAME]

    entities = [
        OkinBedLight(coordinator, device_name),
    ]

    async_add_entities(entities)


class OkinBedLight(LightEntity):
    """Representation of an OKIN bed under-bed light."""

    def __init__(
        self,
        coordinator: OkinBedCoordinator,
        device_name: str,
    ) -> None:
        """Initialize the under-bed light."""
        self.coordinator = coordinator
        self._attr_name = f"{device_name} Under-Bed Light"
        self._attr_unique_id = f"{coordinator.mac_address}_light"
        self._attr_is_on = False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        _LOGGER.info("Turning on under-bed light")
        if await self.coordinator.async_send_command("light_on"):
            self._attr_is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        _LOGGER.info("Turning off under-bed light")
        if await self.coordinator.async_send_command("light_off"):
            self._attr_is_on = False
            self.async_write_ha_state()
