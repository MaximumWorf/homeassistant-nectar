"""Config flow for OKIN Adjustable Bed integration."""

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    CONF_MAC_ADDRESS,
    CONF_DEVICE_NAME,
    CONF_CONNECTION_MODE,
    CONF_API_URL,
    MODE_DIRECT,
    MODE_REMOTE,
    DEVICE_NAME_PATTERNS,
)

_LOGGER = logging.getLogger(__name__)

# Debug logging to verify this version is loaded
_LOGGER.warning("OKIN Bed config_flow.py loading - Version 2.0.7 - Manual entry support")


async def _async_has_devices(hass: HomeAssistant) -> bool:
    """Return if there are devices that can be discovered."""
    # Check for any Bluetooth devices matching OKIN patterns
    discovered = async_discovered_service_info(hass, connectable=True)
    return any(
        any(pattern.lower() in (device.name or "").lower() for pattern in DEVICE_NAME_PATTERNS)
        for device in discovered
    )


class OkinBedConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for OKIN Bed."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_devices: dict[str, BluetoothServiceInfoBleak] = {}
        self._selected_device: BluetoothServiceInfoBleak | None = None
        self._manual_mac: str | None = None
        self._connection_mode: str | None = None
        self._device_name: str | None = None
        self._api_url: str | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - choose discovery or manual."""
        if user_input is not None:
            if user_input.get("setup_type") == "discovered":
                return await self.async_step_discovered()
            else:
                return await self.async_step_manual()

        # Check if any devices discovered
        discovered = async_discovered_service_info(self.hass, connectable=True)
        self._discovered_devices = {
            device.address: device
            for device in discovered
            if any(
                pattern.lower() in (device.name or "").lower()
                for pattern in DEVICE_NAME_PATTERNS
            )
        }

        # Offer both options
        setup_options = {
            "manual": "Manual setup (for remote API or manual entry)",
        }

        if self._discovered_devices:
            setup_options["discovered"] = f"Use discovered device ({len(self._discovered_devices)} found)"

        data_schema = vol.Schema(
            {
                vol.Required("setup_type"): vol.In(setup_options),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
        )

    async def async_step_discovered(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle discovered device selection."""
        errors = {}

        if user_input is not None:
            mac_address = user_input[CONF_MAC_ADDRESS]
            self._selected_device = self._discovered_devices[mac_address]

            # Check if already configured
            await self.async_set_unique_id(mac_address)
            self._abort_if_unique_id_configured()

            # Go to connection mode selection
            return await self.async_step_connection_mode()

        # Create device selection schema
        device_list = {
            device.address: f"{device.name or 'Unknown'} ({device.address})"
            for device in self._discovered_devices.values()
        }

        data_schema = vol.Schema(
            {
                vol.Required(CONF_MAC_ADDRESS): vol.In(device_list),
            }
        )

        return self.async_show_form(
            step_id="discovered",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_manual(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle manual MAC address entry."""
        errors = {}

        if user_input is not None:
            mac_address = user_input[CONF_MAC_ADDRESS].upper()

            # Validate MAC address format
            if not self._is_valid_mac(mac_address):
                errors[CONF_MAC_ADDRESS] = "invalid_mac"
            else:
                # Check if already configured
                await self.async_set_unique_id(mac_address)
                self._abort_if_unique_id_configured()

                # Store MAC and go to connection mode
                self._selected_device = None  # No discovered device
                self._manual_mac = mac_address
                return await self.async_step_connection_mode()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_MAC_ADDRESS): cv.string,
            }
        )

        return self.async_show_form(
            step_id="manual",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "example": "AA:BB:CC:DD:EE:FF"
            },
        )

    def _is_valid_mac(self, mac: str) -> bool:
        """Validate MAC address format."""
        import re
        pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        return bool(re.match(pattern, mac))

    async def async_step_connection_mode(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle connection mode selection."""
        errors = {}

        if user_input is not None:
            self._connection_mode = user_input[CONF_CONNECTION_MODE]

            if self._connection_mode == MODE_REMOTE:
                return await self.async_step_remote_config()
            else:
                return await self.async_step_name()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_CONNECTION_MODE, default=MODE_DIRECT): vol.In(
                    {
                        MODE_DIRECT: "Direct (Bluetooth on this device)",
                        MODE_REMOTE: "Remote (API server on another device)",
                    }
                ),
            }
        )

        return self.async_show_form(
            step_id="connection_mode",
            data_schema=data_schema,
            errors=errors,
        )

    async def async_step_remote_config(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure remote API URL."""
        errors = {}

        if user_input is not None:
            # Validate URL format
            self._api_url = user_input[CONF_API_URL].rstrip("/")

            # TODO: Could add URL validation here
            return await self.async_step_name()

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_API_URL,
                    default="http://192.168.1.100:8000",
                ): cv.string,
            }
        )

        # Build description based on whether we have a discovered device or manual MAC
        if self._selected_device:
            device_desc = f"{self._selected_device.name} ({self._selected_device.address})"
        else:
            device_desc = self._manual_mac or "Manual entry"

        return self.async_show_form(
            step_id="remote_config",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "device": device_desc
            },
        )

    async def async_step_name(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the naming step."""
        errors = {}

        if user_input is not None:
            device_name = user_input[CONF_DEVICE_NAME]

            # Get MAC address from either discovered device or manual entry
            mac_address = self._selected_device.address if self._selected_device else self._manual_mac

            # Build config data
            data = {
                CONF_MAC_ADDRESS: mac_address,
                CONF_DEVICE_NAME: device_name,
                CONF_CONNECTION_MODE: self._connection_mode,
            }

            # Add API URL if in remote mode
            if self._connection_mode == MODE_REMOTE and self._api_url:
                data[CONF_API_URL] = self._api_url

            # Create the config entry
            return self.async_create_entry(
                title=device_name,
                data=data,
            )

        # Default name suggestion
        if self._selected_device:
            suggested_name = self._selected_device.name or "OKIN Bed"
            device_desc = f"{self._selected_device.name} ({self._selected_device.address})"
        else:
            suggested_name = "OKIN Bed"
            device_desc = self._manual_mac or "Manual entry"

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_DEVICE_NAME, default=suggested_name
                ): cv.string,
            }
        )

        return self.async_show_form(
            step_id="name",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "device": device_desc
            },
        )

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> FlowResult:
        """Handle bluetooth discovery."""
        _LOGGER.debug("Discovered OKIN bed: %s", discovery_info)

        # Check if device name matches OKIN patterns
        if not any(
            pattern.lower() in (discovery_info.name or "").lower()
            for pattern in DEVICE_NAME_PATTERNS
        ):
            return self.async_abort(reason="not_supported")

        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        self._selected_device = discovery_info

        return await self.async_step_name()
