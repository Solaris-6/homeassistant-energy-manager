"""Energy Manager integration initialization."""

import logging
from typing import Any, Dict, Optional

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import async_register_platforms

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

    # Register the sensor platform
    await async_register_platforms(
        hass,
        [
            {
                "type": "sensor",
                "domain": DOMAIN,
                "name": NAME + " Power",
                "unique_id": f"{DOMAIN}_power",
                "unit_of_measurement": "kW",
                "device_class": "power",
                "state_class": "measurement",
            }
        ]
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator = hass.data[DOMAIN].get("coordinator")
    if coordinator:
        await coordinator.async_shutdown()

    hass.data[DOMAIN]["unloaded"] = True
    return True


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove an energy manager config entry."""
    coordinator = hass.data[DOMAIN].get("coordinator")
    if coordinator:
        await coordinator.async_shutdown()
