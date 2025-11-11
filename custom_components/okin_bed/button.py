"""Support for OKIN Bed buttons (presets)."""

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    CONF_DEVICE_NAME,
    PRESETS,
    PRESET_FLAT,
    PRESET_ZERO_GRAVITY,
    PRESET_ANTI_SNORE,
    PRESET_TV,
    PRESET_LOUNGE,
)
from .coordinator import OkinBedCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OKIN Bed button entities."""
    coordinator: OkinBedCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    device_name = config_entry.data[CONF_DEVICE_NAME]

    entities = [
        OkinBedPresetButton(coordinator, device_name, preset_id, preset_name)
        for preset_id, preset_name in PRESETS.items()
    ]

    async_add_entities(entities)


class OkinBedPresetButton(ButtonEntity):
    """Representation of an OKIN bed preset button.

    One-time press: Sends single command that moves bed to preset position.
    """

    def __init__(
        self,
        coordinator: OkinBedCoordinator,
        device_name: str,
        preset_id: str,
        preset_name: str,
    ) -> None:
        """Initialize the preset button."""
        self.coordinator = coordinator
        self._preset_id = preset_id
        self._attr_name = f"{device_name} {preset_name}"
        self._attr_unique_id = f"{coordinator.mac_address}_preset_{preset_id}"

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("Activating preset: %s", self._preset_id)

        # Map preset IDs to OkinBed method names
        command_map = {
            PRESET_FLAT: "flat",
            PRESET_ZERO_GRAVITY: "zero_gravity",
            PRESET_ANTI_SNORE: "anti_snore",
            PRESET_TV: "tv_position",
            PRESET_LOUNGE: "lounge",
        }

        command_name = command_map.get(self._preset_id)
        if command_name:
            await self.coordinator.async_send_command(command_name)
        else:
            _LOGGER.error("Unknown preset: %s", self._preset_id)
