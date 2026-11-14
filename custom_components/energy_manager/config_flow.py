"""Config flow for Energy Manager."""

import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    NAME,
    DEFAULT_THRESHOLD_KW,
    DEFAULT_ISOSTERISIS_S,
    MAX_POWER_KW,
    MIN_POWER_KW,
)

_LOGGER = logging.getLogger(__name__)


def default_device_list():
    """Return the list of default devices with typical configuration."""
    return [
        {
            "device_id": "frigorifero",
            "entity_id": "",
            "priority": 100,
            "area": "Cucina",
            "description": "Frigorifero Samsung",
            "power_estimate": 0.07,
            "power_limit": 0.1,
        },
        {
            "device_id": "condizionatore",
            "entity_id": "switch.quadro_elettrico_primo_piano_sy2_condizionatore_interruttore",
            "priority": 60,
            "area": "Sala Pranzo",
            "description": "Condizionatore Zephir 9000BTU",
            "power_estimate": 1.0,
            "power_limit": 1.2,
        },
        {
            "device_id": "scaldabagno",
            "entity_id": "switch.quadro_elettrico_primo_piano_sy2_scaldabagno_interruttore",
            "priority": 80,
            "area": "Bagno",
            "description": "Scaldabagno",
            "power_estimate": 1.1,
            "power_limit": 1.5,
        },
        {
            "device_id": "lavastoviglie",
            "entity_id": "switch.quadro_elettrico_primo_piano_sy2_lavastoviglie_interruttore",
            "priority": 70,
            "area": "Cucina",
            "description": "Lavastoviglie Indesit",
            "power_estimate": 1.5,
            "power_limit": 2.0,
        },
        {
            "device_id": "lavatrice",
            "entity_id": "switch.quadro_elettrico_primo_piano_sy2_lavatrice_interruttore",
            "priority": 60,
            "area": "Cucina",
            "description": "Lavatrice Indesit",
            "power_estimate": 1.5,
            "power_limit": 2.0,
        },
    ]


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Energy Manager."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step to collect basic settings."""
        if not user_input:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required("threshold_kW", default=DEFAULT_THRESHOLD_KW): vol.Range(min=MIN_POWER_KW, max=MAX_POWER_KW),
                    vol.Required("isosterisis_s", default=DEFAULT_ISOSTERISIS_S): vol.Range(min=5, max=300),
                }),
                errors={},
            )

        # Validate threshold
        threshold = float(user_input.get("threshold_kW", 0))
        isosterisis = int(float(user_input.get("isosterisis_s", 0)))

        if MIN_POWER_KW <= threshold <= MAX_POWER_KW and isosterisis > 0:
            return await self.async_step_devices()
        else:
            self.errors["base"] = "invalid_threshold"
            defaults = {
                "threshold_kW": DEFAULT_THRESHOLD_KW,
                "isosterisis_s": DEFAULT_ISOSTERISIS_S,
            }
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required("threshold_kW", default=DEFAULT_THRESHOLD_KW): vol.Range(min=MIN_POWER_KW, max=MAX_POWER_KW),
                    vol.Required("isosterisis_s", default=DEFAULT_ISOSTERISIS_S): vol.Range(min=5, max=300),
                }),
                errors={},
            )

    async def async_step_devices(self, user_input=None):
        """Handle device configuration step."""
        if not user_input:
            return self.async_show_form(
                step_id="devices",
                data_schema=vol.Schema({
                    vol.Required("general_breaker"): str,
                }),
                errors={},
            )

        general_breaker = user_input.get("general_breaker", "switch.quadro_elettrico_primo_piano_sy2_misure_interruttore")

        # Create entry with all collected data (devices configured later via UI)
        config_data = {
            "threshold_kW": float(user_input["threshold_kW"]),
            "isosterisis_s": int(float(user_input.get("isosterisis_s", DEFAULT_ISOSTERISIS_S))),
            "general_breaker": general_breaker,
            "devices": [],  # Will be populated via UI
        }

        return self.async_create_entry(title=NAME, data=config_data)
