"""Support for OKIN Bed switches."""

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up OKIN Bed switch entities."""
    coordinator: OkinBedCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    device_name = config_entry.data[CONF_DEVICE_NAME]

    entities = [
        OkinBedMassageSwitch(coordinator, device_name),
    ]

    async_add_entities(entities)


class OkinBedMassageSwitch(SwitchEntity):
    """Representation of an OKIN bed massage switch."""

    def __init__(
        self,
        coordinator: OkinBedCoordinator,
        device_name: str,
    ) -> None:
        """Initialize the massage switch."""
        self.coordinator = coordinator
        self._attr_name = f"{device_name} Massage"
        self._attr_unique_id = f"{coordinator.mac_address}_massage"
        self._attr_is_on = False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on massage."""
        _LOGGER.info("Turning on massage")
        if await self.coordinator.async_send_command("massage_on"):
            self._attr_is_on = True
            self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off massage."""
        _LOGGER.info("Turning off massage")
        if await self.coordinator.async_send_command("massage_off"):
            self._attr_is_on = False
            self.async_write_ha_state()
