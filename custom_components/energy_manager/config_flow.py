"""Config flow for Energy Manager."""

import logging
from typing import Any, Dict, List, Optional

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
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
    """Handle a config flow for Energy Manager."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step to collect basic settings."""
        if user_input is not None:
            # Validate threshold
            if (
                "threshold_kW" in user_input
                and "isosterisis_s" in user_input
                and MIN_POWER_KW <= float(user_input["threshold_kW"]) <= MAX_POWER_KW
                and float(user_input.get("isosterisis_s", DEFAULT_ISOSTERISIS_S)) > 0
            ):
                # Move to device configuration step
                return await self.async_step_devices()

            if user_input:
                self.errors["base"] = "invalid_threshold"

        defaults = {
            "threshold_kW": DEFAULT_THRESHOLD_KW,
            "isosterisis_s": DEFAULT_ISOSTERISIS_S,
        }

        return self.async_show_form(
            step_id="user",
            data_schema=self.build_user_schema(defaults),
            errors={},
        )

    async def async_step_devices(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle device configuration step."""
        if not user_input:
            return await self.async_step_devices_confirm()

        # Collect and validate devices
        general_breaker = user_input.get("general_breaker", "switch.quadro_elettrico_primo_piano_sy2_misure_interruttore")
        devices = user_input.get("devices", [])

        if not isinstance(devices, list) or len(devices) == 0:
            self.errors["base"] = "invalid_devices"
            defaults = {
                "general_breaker": general_breaker,
                "devices": default_device_list(),
            }
            return self.async_show_form(
                step_id="devices",
                data_schema=self.build_devices_schema(defaults),
                errors={},
            )

        # Create entry with all collected data
        config_data = {
            "threshold_kW": float(user_input["threshold_kW"]),
            "isosterisis_s": int(float(user_input.get("isosterisis_s", DEFAULT_ISOSTERISIS_S))),
            "general_breaker": general_breaker,
            "devices": devices,
        }

        return self.async_create_entry(title=NAME, data=config_data)

    async def async_step_devices_confirm(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Show device configuration form."""
        defaults = {
            "general_breaker": "switch.quadro_elettrico_primo_piano_sy2_misure_interruttore",
            "devices": default_device_list(),
        }

        return self.async_show_form(
            step_id="devices_confirm",
            data_schema=self.build_devices_schema(defaults),
            errors={},
        )

    @staticmethod
    def build_user_schema(defaults: Dict[str, Any]) -> selector.SelectorSchema:
        """Build user configuration schema."""
        return selector.SelectorSchema({
            "threshold_kW": selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=MIN_POWER_KW,
                    max=MAX_POWER_KW,
                    step=0.1,
                    unit_of_measurement="kW",
                    suggested_value=float(defaults.get("threshold_kW", DEFAULT_THRESHOLD_KW)),
                )
            ),
            "isosterisis_s": selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=5,
                    max=300,
                    step=5,
                    unit_of_measurement="seconds",
                    suggested_value=float(defaults.get("isosterisis_s", DEFAULT_ISOSTERISIS_S)),
                )
            ),
        })

    @staticmethod
    def build_devices_schema(defaults: Dict[str, Any]) -> selector.SelectorSchema:
        """Build devices configuration schema."""
        return selector.SelectorSchema({
            "general_breaker": selector.TextSelector(
                selector.TextSelectorConfig(placeholder="Interruttore generale")
            ),
            "devices": selector.ObjectSelector(),
        })


def default_device_list() -> List[Dict[str, Any]]:
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
