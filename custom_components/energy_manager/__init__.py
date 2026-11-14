"""Energy Manager integration initialization."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_component import EntityComponent

from .const import DOMAIN, NAME

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Energy Manager integration."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Energy Manager from a config entry."""
    coordinator = hass.data[DOMAIN].get("coordinator")
    if not coordinator:
        from .coordinator import EnergyManagerCoordinator
        coordinator = EnergyManagerCoordinator(hass, entry)
        hass.data[DOMAIN]["coordinator"] = coordinator

    component = EntityComponent(hass, NAME, DOMAIN, entry)
    await component.async_add_entities([coordinator.sensor])
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator = hass.data[DOMAIN].get("coordinator")
    if coordinator:
        await coordinator.async_shutdown()
    return True

