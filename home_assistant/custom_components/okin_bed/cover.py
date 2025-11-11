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

from .const import DOMAIN, CONF_DEVICE_NAME, MOVEMENT_COMMAND_INTERVAL
from .coordinator import OkinBedCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up OKIN Bed cover entities."""
    coordinator: OkinBedCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    device_name = config_entry.data[CONF_DEVICE_NAME]

    entities = [
        OkinBedSection(coordinator, device_name, "head", "Head"),
        OkinBedSection(coordinator, device_name, "lumbar", "Lumbar"),
        OkinBedSection(coordinator, device_name, "foot", "Foot"),
    ]

    async_add_entities(entities)


class OkinBedSection(CoverEntity):
    """Representation of an OKIN bed section as a cover.

    Press and hold behavior: Repeatedly sends commands while user holds button.
    """

    _attr_device_class = CoverDeviceClass.AWNING
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
    )

    def __init__(
        self,
        coordinator: OkinBedCoordinator,
        device_name: str,
        section: str,
        section_name: str,
    ) -> None:
        """Initialize the bed section cover."""
        self.coordinator = coordinator
        self._section = section
        self._attr_name = f"{device_name} {section_name}"
        self._attr_unique_id = f"{coordinator.mac_address}_{section}"
        self._movement_id_up = f"{section}_up"
        self._movement_id_down = f"{section}_down"
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
        # OKIN beds don't provide position feedback
        return None

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the cover (raise section).

        Starts continuous movement that repeats commands while held.
        """
        _LOGGER.info("Opening %s section (press and hold)", self._section)
        self._is_opening = True
        self._is_closing = False
        self.async_write_ha_state()

        # Start continuous movement
        await self.coordinator.async_start_continuous_movement(
            self._movement_id_up,
            f"{self._section}_up",
            MOVEMENT_COMMAND_INTERVAL,
        )

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the cover (lower section).

        Starts continuous movement that repeats commands while held.
        """
        _LOGGER.info("Closing %s section (press and hold)", self._section)
        self._is_closing = True
        self._is_opening = False
        self.async_write_ha_state()

        # Start continuous movement
        await self.coordinator.async_start_continuous_movement(
            self._movement_id_down,
            f"{self._section}_down",
            MOVEMENT_COMMAND_INTERVAL,
        )

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        _LOGGER.info("Stopping %s section", self._section)
        self._is_opening = False
        self._is_closing = False
        self.async_write_ha_state()

        # Stop continuous movements for this section
        await self.coordinator.async_stop_continuous_movement(self._movement_id_up)
        await self.coordinator.async_stop_continuous_movement(self._movement_id_down)

        # Send stop command to bed
        await self.coordinator.async_send_command("stop")
