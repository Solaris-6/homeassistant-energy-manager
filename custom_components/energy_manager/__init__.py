"""Energy Manager integration initialization."""

import logging
from typing import Any, Dict, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, NAME
from .coordinator import EnergyManagerCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Energy Manager integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Energy Manager from a config entry."""
    coordinator = hass.data[DOMAIN].get("coordinator")
    if not coordinator:
        coordinator = EnergyManagerCoordinator(hass, entry)
        hass.data[DOMAIN]["coordinator"] = coordinator

    # Forward setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator = hass.data[DOMAIN].get("coordinator")
    if coordinator:
        await coordinator.async_shutdown()

    await hass.config_entries.async_forward_entry_unload(entry, "sensor")

    hass.data[DOMAIN]["unloaded"] = True
    return True


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove an energy manager config entry."""
    coordinator = hass.data[DOMAIN].get("coordinator")
    if coordinator:
        await coordinator.async_shutdown()
