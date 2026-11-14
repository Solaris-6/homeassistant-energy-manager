"""Sensor for Energy Manager."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN,
    NAME,
    STATUS_OK,
    STATUS_WARNING,
    STATUS_CRITICAL,
    STATUS_ERROR,
)

class EnergyManagerSensor(SensorEntity):
    """Sensor for Energy Manager."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        self.coordinator = coordinator
        self._attr_name = f"{NAME} Power"
        self._attr_unique_id = f"{DOMAIN}_power"
        self._attr_unit_of_measurement = "kW"
        self._attr_device_class = "power"
        self._attr_state_class = "measurement"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.coordinator.power_kw

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        attrs = {
            "status": self.coordinator.status,
            "threshold_kW": self.coordinator.threshold_kW,
            "isosterisis_s": self.coordinator.isosterisis_s,
            "total_devices": len(self.coordinator.devices_config),
            "last_action": self.coordinator._last_action,
            "mode": self.coordinator._mode,
            "priority_min": self.coordinator._priority_min,
        }
        return attrs

    @property
    def device_info(self):
        """Return the device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, "energy_manager")},
            name=NAME,
            manufacturer="Home Assistant",
            model="Energy Manager",
        )

    def update(self):
        """Update the sensor."""
        self.coordinator.async_update()

