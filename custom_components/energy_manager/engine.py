import logging
from .const import *

_LOGGER = logging.getLogger(__name__)

class EnergyManagerEngine:
    def __init__(self, hass, config):
        self.hass = hass
        self.config = config
        self.devices = config.get('devices', [])
        self.threshold_kW = config.get('threshold_kW', 2.8)
        self.general_breaker = config.get('general_breaker', 'switch.quadro_elettrico_primo_piano_sy2_misure_interruttore')
        self.devices_dict = {}
        for d in self.devices:
            eid = d.get('entity_id')
            self.devices_dict[eid] = {
                'name': d.get('name', eid),
                'priority': d.get('priority', 50),
                'entity_id': eid,
                'power_estimate': d.get('power_estimate', 0),
                'state': STATE_OFF
            }
        self._current_power_kw = 0.0
        self._target_power_kw = self.threshold_kW
        self._hysteresis_timer = 0
        self._hysteresis_active = False
        self._status = STATUS_OK
        self._action_history = []
        self._device_states = {}
        self._mode = 'normal'
        self._is_vacation_mode = False
        self._is_night_mode = False
        self._is_solar_mode = False
        self._priority_min = 0
        _LOGGER.info('Engine initialized')

    @property
    def status(self):
        return self._status

    @property
    def power_kw(self):
        return self._current_power_kw

    @property
    def target_power_kw(self):
        return self._target_power_kw

    def set_mode(self, mode, **kwargs):
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

    async def async_update(self):
        result = {'action': 'none', 'devices_cut': [], 'devices_restored': [], 'power_before': self._current_power_kw, 'target_power': self._target_power_kw, 'status': self._status, 'reason': '', 'timestamp': datetime.now().isoformat()}
        try:
            power_sensor = 'sensor.quadro_elettrico_primo_piano_smart_meter_potenza_totale'
            state = self.hass.states.get(power_sensor)
            if state:
                self._current_power_kw = float(state.state)
            else:
                _LOGGER.warning('Power sensor not found')
                return result
            for eid, dev in self.devices_dict.items():
                st = self.hass.states.get(eid)
                dev_state = st.state if st else STATE_OFF
                dev['state'] = dev_state
                self._device_states[eid] = dev_state
            if self._should_shed():
                actions = self._shed_non_critical()
                result['action'] = 'shedding'
                result['devices_cut'] = actions
                result['reason'] = 'Potenza eccessiva, shedding non prioritari'
            elif self._should_restore():
                actions = self._restore_devices()
                result['action'] = 'restoring'
                result['devices_restored'] = actions
                result['reason'] = 'Potenza tornata sotto soglia'
            else:
                result['reason'] = 'Potenza nella soglia'
                self._status = STATUS_OK
            if self._current_power_kw > MAX_POWER_KW + 0.5:
                self._status = STATUS_CRITICAL
            elif self._current_power_kw > self.threshold_kW:
                self._status = STATUS_WARNING
            else:
                self._status = STATUS_OK
            return result
        except Exception as err:
            _LOGGER.error('Error in engine update: %s', err)
            self._status = STATUS_ERROR
            return result

    def _should_shed(self):
        return False

    def _should_restore(self):
        return False

    def _shed_non_critical(self):
        return []

    def _restore_devices(self):
        return []

    def get_device_state(self, entity_id):
        return self._device_states.get(entity_id, STATE_UNKNOWN)
