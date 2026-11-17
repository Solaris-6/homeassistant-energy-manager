"""Config flow for Energy Manager."""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries

from .const import (
    DOMAIN,
    NAME,
    DEFAULT_THRESHOLD_KW,
    DEFAULT_ISOSTERISIS_S,
    MAX_POWER_KW,
    MIN_POWER_KW,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_GENERAL_BREAKER = "switch.quadro_elettrico_primo_piano_sy2_misure_interruttore"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Energy Manager."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._threshold_kw: float = DEFAULT_THRESHOLD_KW
        self._isosterisis_s: int = DEFAULT_ISOSTERISIS_S

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle the initial step to collect basic settings."""
        _LOGGER.debug("async_step_user called with input: %s", user_input)

        if user_input is not None:
            try:
                threshold = float(user_input.get("threshold_kW", DEFAULT_THRESHOLD_KW))
                isosterisis = int(float(user_input.get("isosterisis_s", DEFAULT_ISOSTERISIS_S)))
            except (ValueError, TypeError) as err:
                _LOGGER.error("Invalid input values: %s", err)
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema({
                        vol.Required("threshold_kW", default=DEFAULT_THRESHOLD_KW): float,
                        vol.Required("isosterisis_s", default=DEFAULT_ISOSTERISIS_S): int,
                    }),
                    errors={"base": "invalid_input"},
                )

            if MIN_POWER_KW <= threshold <= MAX_POWER_KW and isosterisis > 0:
                self._threshold_kw = threshold
                self._isosterisis_s = isosterisis
                return await self.async_step_devices()
            else:
                return self.async_show_form(
                    step_id="user",
                    data_schema=vol.Schema({
                        vol.Required("threshold_kW", default=DEFAULT_THRESHOLD_KW): float,
                        vol.Required("isosterisis_s", default=DEFAULT_ISOSTERISIS_S): int,
                    }),
                    errors={"base": "invalid_threshold"},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("threshold_kW", default=DEFAULT_THRESHOLD_KW): float,
                vol.Required("isosterisis_s", default=DEFAULT_ISOSTERISIS_S): int,
            }),
            errors={},
        )

    async def async_step_devices(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle device configuration step."""
        _LOGGER.debug("async_step_devices called with input: %s", user_input)

        if user_input is not None:
            general_breaker = user_input.get("general_breaker", DEFAULT_GENERAL_BREAKER)

            config_data: Dict[str, Any] = {
                "threshold_kW": self._threshold_kw,
                "isosterisis_s": self._isosterisis_s,
                "general_breaker": general_breaker,
                "devices": [],
            }

            _LOGGER.info("Creating config entry with data: %s", config_data)
            return self.async_create_entry(title=NAME, data=config_data)

        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema({
                vol.Required("general_breaker", default=DEFAULT_GENERAL_BREAKER): str,
            }),
            errors={},
        )

    async def async_step_reconfigure(self, user_input: Optional[Dict[str, Any]] = None):
        """Handle reconfiguration of the integration."""
        if user_input is not None:
            config_data: Dict[str, Any] = {
                "threshold_kW": float(user_input.get("threshold_kW", self._threshold_kw)),
                "isosterisis_s": int(float(user_input.get("isosterisis_s", self._isosterisis_s))),
                "general_breaker": user_input.get("general_breaker", DEFAULT_GENERAL_BREAKER),
                "devices": [],
            }
            return self.async_create_entry(title=NAME, data=config_data)

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema({
                vol.Required("threshold_kW", default=self._threshold_kw): float,
                vol.Required("isosterisis_s", default=self._isosterisis_s): int,
                vol.Required("general_breaker", default=DEFAULT_GENERAL_BREAKER): str,
            }),
            errors={},
        )