"""Coordinator for the Energy Manager integration."""

import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import (
    DOMAIN,
    NAME,
    DEFAULT_THRESHOLD_KW,
    DEFAULT_ISOSTERISIS_S,
    MAX_POWER_KW,
    MIN_POWER_KW,
    PRIORITY_HIGHEST,
    PRIORITY_HIGH,
    PRIORITY_MEDIUM,
    PRIORITY_LOW,
    PRIORITY_LOWEST,
    STATUS_OK,
    STATUS_WARNING,
    STATUS_CRITICAL,
    STATUS_ERROR,
    STATE_ON,
    STATE_OFF,
    STATE_PAUSED,
    STATE_UNKNOWN,
)

_LOGGER = logging.getLogger(__name__)


class EnergyManagerCoordinator(DataUpdateCoordinator):
    """Coordinate the energy management logic."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.hass = hass
        self.config_entry = entry
        self.threshold_kW = entry.data.get("threshold_kW", DEFAULT_THRESHOLD_KW)
        self.isosterisis_s = int(float(entry.data.get("isosterisis_s", DEFAULT_ISOSTERISIS_S)))

        # Device configuration (priority order)
        self.devices: List[Dict[str, Any]] = entry.data.get("devices", [])

        # Track current state
        self._current_power_kw: float = 0.0
        self._status: str = STATUS_OK
        self._last_action: Optional[Dict] = None
        self._action_history: List[Dict] = []

        # Initialize the general breaker (non-sheddable)
        self.general_breaker: str = entry.data.get("general_breaker", "switch.quadro_elettrico_primo_piano_sy2_misure_interruttore")

        super().__init__(hass, logger=_LOGGER, name=DOMAIN, update_interval=timedelta(seconds=1))

    @property
    def power_kw(self) -> float:
        """Return current power consumption in kW."""
        return self._current_power_kw

    @property
    def status(self) -> str:
        """Return the current status."""
        return self._status

    @property
    def devices_config(self) -> list:
        """Return the configured devices."""
        return self.devices

    def async_update_devices(self) -> None:
        """Update device states."""
        for device in self.devices:
            entity_id = device.get("entity_id")
            if entity_id and isinstance(entity_id, str):
                state = self.hass.states.get(entity_id)
                device["state"] = state.state if state else STATE_UNKNOWN

    def async_check_and_shed(self) -> dict:
        """Check power and shed non-critical loads if needed.
        
        Returns a dict with the result of the operation.
        """
        result: dict = {
            "action": "none",
            "devices_cut": [],
            "devices_restored": [],
            "power_before": self._current_power_kw,
            "power_threshold": self.threshold_kW,
            "reason": ""
        }

        # If power is below threshold, do nothing (or restore devices)
        if self._current_power_kw <= self.threshold_kW:
            result["reason"] = "Power below threshold"
            return result

        # Sort devices by priority (LOWEST priority first = shed first)
        # Priority: 100=Highest (never shed), 10=Lowest (shed first)
        sorted_devices = sorted(self.devices, key=lambda d: d.get("priority", 0))

        # Track how many devices we shed
        devices_shed_count = 0

        # Shed devices starting from lowest priority
        for device in sorted_devices:
            priority = device.get("priority", 0)
            entity_id = device.get("entity_id")
            
            if not entity_id or not isinstance(entity_id, str):
                continue
                
            # Never shed the general breaker
            if entity_id == self.general_breaker:
                continue
            
            # Never shed devices with priority >= 90 (critical - frigorifero)
            if priority >= 90:
                continue
            
            # Check if device is currently ON
            state = self.hass.states.get(entity_id)
            if not state or state.state != STATE_ON:
                continue

            self.hass.call_service("switch/turn_off", entity_id=entity_id)
            result["devices_cut"].append(entity_id)
            devices_shed_count += 1
            _LOGGER.info("Shed device: %s (priority: %d)", entity_id, priority)
            
            # Shed only one device at a time to avoid overshooting
            break

        # Update status based on power level
        if self._current_power_kw > MAX_POWER_KW + 0.5:
            self._status = STATUS_CRITICAL
        elif self._current_power_kw > self.threshold_kW:
            self._status = STATUS_WARNING
        else:
            self._status = STATUS_OK

        if devices_shed_count > 0:
            result["action"] = "shedding"
            result["reason"] = f"Shed {devices_shed_count} non-critical device(s)"
        else:
            result["reason"] = "No shedable devices found"

        result["status"] = self._status
        return result

    async def async_update(self) -> None:
        """Fetch new state data for the coordinator."""
        try:
            power_sensor = "sensor.quadro_elettrico_primo_piano_smart_meter_potenza_totale"
            state = self.hass.states.get(power_sensor)
            if state:
                self._current_power_kw = float(state.state)
            else:
                _LOGGER.warning("Power sensor not found: %s", power_sensor)
                self._current_power_kw = 0.0

            self.async_update_devices()
            result = self.async_check_and_shed()
            self._last_action = result

            _LOGGER.debug(
                "Power: %.2f kW, Status: %s, Devices: %d, Action: %s",
                self._current_power_kw,
                self._status,
                len(self.devices),
                result.get("action")
            )

        except Exception as err:
            raise UpdateFailed(f"Error updating energy manager: {err}")
