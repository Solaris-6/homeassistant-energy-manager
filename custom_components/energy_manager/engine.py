"""Energy Manager Engine - Gestione avanzata della potenza."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

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


class EnergyManagerEngine:
    """Engine per la gestione avanzata della potenza."""

    def __init__(self, hass: Any, config: Dict[str, Any]) -> None:
        self.hass = hass
        self.config = config
        self.devices: List[Dict] = config.get('devices', [])
        self.threshold_kW: float = config.get('threshold_kW', DEFAULT_THRESHOLD_KW)
        self.general_breaker: str = config.get('general_breaker', 'switch.quadro_elettrico_primo_piano_sy2_misure_interruttore')

        # Build device dictionary
        self.devices_dict: Dict[str, Dict] = {}
        for d in self.devices:
            eid = d.get('entity_id', '')
            if eid and isinstance(eid, str):
                self.devices_dict[eid] = {
                    'name': d.get('name', eid),
                    'priority': d.get('priority', 50),
                    'entity_id': eid,
                    'power_estimate': float(d.get('power_estimate', 0)),
                    'state': STATE_OFF
                }

        self._current_power_kw: float = 0.0
        self._target_power_kw: float = self.threshold_kW
        self._hysteresis_timer: int = 0
        self._hysteresis_active: bool = False
        self._status: str = STATUS_OK
        self._action_history: List[Dict] = []
        self._device_states: Dict[str, str] = {}
        self._mode: str = 'normal'
        self._is_vacation_mode: bool = False
        self._is_night_mode: bool = False
        self._is_solar_mode: bool = False
        self._priority_min: int = 0

        _LOGGER.info('Engine initialized with %d devices', len(self.devices))

    @property
    def status(self) -> str:
        """Return current status."""
        return self._status

    @property
    def power_kw(self) -> float:
        """Return current power in kW."""
        return self._current_power_kw

    @property
    def target_power_kw(self) -> float:
        """Return target power in kW."""
        return self._target_power_kw

    @property
    def mode(self) -> str:
        """Return current mode."""
        return self._mode

    def set_mode(self, mode: str, **kwargs: Any) -> None:
        """Set special operation mode."""
        self._mode = mode
        
        if mode == 'vacation':
            self._is_vacation_mode = True
            self._priority_min = 50
        elif mode == 'night':
            self._is_night_mode = True
            self._priority_min = 50
        elif mode == 'solar':
            self._is_solar_mode = True
            self._target_power_kw = self.threshold_kW * 2
        elif mode == 'emergenza':
            self._priority_min = 90
        else:
            self._priority_min = 0

        _LOGGER.info("Mode changed to: %s", mode)

    async def async_update(self) -> Dict[str, Any]:
        """Update engine state."""
        result: Dict[str, Any] = {
            'action': 'none',
            'devices_cut': [],
            'devices_restored': [],
            'power_before': self._current_power_kw,
            'target_power': self._target_power_kw,
            'status': self._status,
            'reason': '',
            'timestamp': datetime.now().isoformat()
        }

        try:
            power_sensor = 'sensor.quadro_elettrico_primo_piano_smart_meter_potenza_totale'
            state = self.hass.states.get(power_sensor) if hasattr(self.hass, 'states') else None
            
            if state and state.state:
                self._current_power_kw = float(state.state)
            else:
                _LOGGER.warning('Power sensor not found or no state')
                return result

            # Update device states
            for eid, dev in self.devices_dict.items():
                st = self.hass.states.get(eid) if hasattr(self.hass, 'states') else None
                if st and st.state:
                    dev_state = st.state
                else:
                    dev_state = STATE_OFF
                
                dev['state'] = dev_state
                self._device_states[eid] = dev_state

            # Check if shedding is needed
            if self._current_power_kw > MAX_POWER_KW + 0.5 or self._current_power_kw > self.threshold_kW:
                actions = self._shed_non_critical()
                result['action'] = 'shedding'
                result['devices_cut'] = actions
                result['reason'] = f'Potenza eccessiva ({self._current_power_kw:.1f} kW), shedding non prioritari'
            else:
                # Check if devices can be restored
                actions = self._restore_devices()
                result['action'] = 'restoring' if actions else 'none'
                result['devices_restored'] = actions
                result['reason'] = 'Potenza tornata sotto soglia' if actions else 'Potenza nella soglia'

            # Update status
            if self._current_power_kw > MAX_POWER_KW + 0.5:
                self._status = STATUS_CRITICAL
            elif self._current_power_kw > self.threshold_kW:
                self._status = STATUS_WARNING
            else:
                self._status = STATUS_OK

            return result

        except Exception as err:
            _LOGGER.error('Error in engine update: %s', str(err))
            self._status = STATUS_ERROR
            return result

    def get_device_state(self, entity_id: Optional[str]) -> Optional[str]:
        """Get state of a specific device."""
        if not entity_id or not isinstance(entity_id, str):
            return None
        return self._device_states.get(entity_id, STATE_UNKNOWN)

    def get_all_devices(self) -> List[Dict]:
        """Return all configured devices with their states."""
        result = []
        for eid, dev in self.devices_dict.items():
            result.append({
                'entity_id': eid,
                'name': dev['name'],
                'priority': dev['priority'],
                'state': dev.get('state', STATE_UNKNOWN),
                'power_estimate': dev.get('power_estimate', 0)
            })
        return sorted(result, key=lambda d: d['priority'], reverse=True)

    def _should_shed(self) -> bool:
        """Check if shedding is needed."""
        return self._current_power_kw > MAX_POWER_KW + 0.5 and not self._is_vacation_mode

    def _should_restore(self) -> bool:
        """Check if devices can be restored."""
        return self._status == STATUS_OK or self._status == STATUS_WARNING

    def _shed_non_critical(self) -> List[str]:
        """Shed non-critical devices."""
        shed_list = []
        
        # Sort by priority (lowest first)
        sorted_devices = sorted(
            self.devices_dict.items(),
            key=lambda x: x[1]['priority']
        )
        
        for eid, dev in sorted_devices:
            if not eid or not isinstance(eid, str):
                continue
            
            priority = dev['priority']
            
            # Never shed general breaker
            if eid == self.general_breaker:
                continue
            
            # Never shed critical devices (priority >= 90)
            if priority >= PRIORITY_HIGH:
                continue
            
            # Check if device is ON before shedding
            state = dev.get('state', STATE_UNKNOWN)
            if state != STATE_ON:
                continue

            self.hass.call_service(
                'switch/turn_off',
                entity_id=eid
            ) if hasattr(self.hass, 'call_service') else None
            
            shed_list.append(eid)
            
            # Shed only one device at a time
            break
        
        return shed_list

    def _restore_devices(self) -> List[str]:
        """Restore devices that were previously shed."""
        restored = []
        
        for eid, dev in self.devices_dict.items():
            if not eid or not isinstance(eid, str):
                continue
            
            priority = dev['priority']
            
            # Never restore general breaker
            if eid == self.general_breaker:
                continue
            
            # Only restore non-critical devices first (highest priority)
            if priority < PRIORITY_MEDIUM:  # Skip critical devices initially
                continue

            state = dev.get('state', STATE_UNKNOWN)
            if state != STATE_OFF:
                continue

            self.hass.call_service(
                'switch/turn_on',
                entity_id=eid
            ) if hasattr(self.hass, 'call_service') else None
            
            restored.append(eid)
        
        return restored
