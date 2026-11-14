"""Config flow for Energy Manager."""

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    NAME,
    DEFAULT_THRESHOLD_KW,
    DEFAULT_ISOSTERISIS_S,
    MAX_POWER_KW,
    MIN_POWER_KW,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Energy Manager."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            if user_input["threshold_kW"] < MIN_POWER_KW or user_input["threshold_kW"] > MAX_POWER_KW:
                self.errors["base"] = "invalid_threshold"
            else:
                return self.async_create_entry(title=NAME, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("threshold_kW", default=DEFAULT_THRESHOLD_KW): vol.Number(
                    description={"suggested_value": DEFAULT_THRESHOLD_KW, "min": MIN_POWER_KW, "max": MAX_POWER_KW}
                ),
                vol.Required("isosterisis_s", default=DEFAULT_ISOSTERISIS_S): vol.Number(
                    description={"suggested_value": DEFAULT_ISOSTERISIS_S}
                ),
            }),
            errors={},
        )

    async def async_step_devices(self, user_input=None):
        """Handle device configuration step."""
        if user_input is not None:
            return self.async_create_entry(title=NAME, data=user_input)

        default_devices = [
            {
                "device_id": "frigorifero",
                "entity_id": "",
                "priority": 100,
                "area": "Cucina",
                "description": "Frigorifero Samsung",
                "power_estimate": 0.07,
                "power_limit": 0.1
            },
            {
                "device_id": "condizionatore",
                "entity_id": "switch.quadro_elettrico_primo_piano_sy2_condizionatore_interruttore",
                "priority": 60,
                "area": "Sala Pranzo",
                "description": "Condizionatore Zephir 9000BTU",
                "power_estimate": 1.0,
                "power_limit": 1.2
            },
            {
                "device_id": "scaldabagno",
                "entity_id": "switch.quadro_elettrico_primo_piano_sy2_scaldabagno_interruttore",
                "priority": 80,
                "area": "Bagno",
                "description": "Scaldabagno",
                "power_estimate": 1.1,
                "power_limit": 1.5
            },
            {
                "device_id": "lavastoviglie",
                "entity_id": "switch.quadro_elettrico_primo_piano_sy2_lavastoviglie_interruttore",
                "priority": 70,
                "area": "Cucina",
                "description": "Lavastoviglie Indesit",
                "power_estimate": 1.5,
                "power_limit": 2.0
            },
            {
                "device_id": "lavatrice",
                "entity_id": "switch.quadro_elettrico_primo_piano_sy2_lavatrice_interruttore",
                "priority": 60,
                "area": "Cucina",
                "description": "Lavatrice Indesit",
                "power_estimate": 1.5,
                "power_limit": 2.0
            }
        ]

        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema({
                vol.Required("general_breaker", default="switch.quadro_elettrico_primo_piano_sy2_misure_interruttore"): str,
                vol.Required("devices", default=default_devices): selector.ObjectSelector(),
            }),
            errors={},
        )

    async def async_step_user_confirm(self, user_input=None):
        """Handle confirmation step."""
        return self.async_create_entry(title=NAME, data=user_input)