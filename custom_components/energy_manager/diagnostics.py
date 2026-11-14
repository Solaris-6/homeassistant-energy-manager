"""Diagnostica Avanzata per Energy Manager."""

import logging
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class DiagnosticsManager:
    def __init__(self, hass: HomeAssistant, config: dict):
        self.hass = hass
        self.config = config
        self.device_health = {}
    async def async_check_device_health(self, devices: list) -> dict:
        health_report = {
            'timestamp': datetime.now().isoformat(),
            'total_devices': len(devices),
            'online': 0,
            'offline': 0,
            'unknown': 0,
            'devices': []
        }

        for device in devices:
            entity_id = device.get('entity_id')
            device_name = device.get('name', entity_id)

            if not entity_id:
                health_report['devices'].append({
                    'entity_id': entity_id,
                    'name': device_name,
                    'status': 'unknown',
                    'last_seen': None,
                    'issue': 'Entity ID non configurato'
                })
                health_report['unknown'] += 1
                continue

            state = self.hass.states.get(entity_id)

            if state is None:
                health_report['devices'].append({
                    'entity_id': entity_id,
                    'name': device_name,
                    'status': 'offline',
                    'last_seen': None,
                    'issue': 'Entità non trovata in Home Assistant'
                })
                health_report['offline'] += 1
                continue

            last_changed = state.last_changed
            if last_changed:
                time_since = datetime.now() - last_changed.replace(tzinfo=None)
                if time_since > timedelta(seconds=self.offline_threshold):
                    health_report['devices'].append({
                        'entity_id': entity_id,
                        'name': device_name,
                        'status': 'offline',
                        'last_seen': last_changed.isoformat(),
                        'issue': f'Nessun aggiornamento da {int(time_since.total_seconds())} secondi'
                    })
                    health_report['offline'] += 1
                    continue

            health_report['devices'].append({
                'entity_id': entity_id,
                'name': device_name,
                'status': state.state,
                'last_seen': last_changed.isoformat() if last_changed else None,
                'issue': None
            })
            health_report['online'] += 1

        self.last_check = datetime.now()
        self.device_health = health_report
        return health_report

    def get_device_health_summary(self) -> dict:
        if not self.device_health:
            return {
                'total_devices': 0,
                'online': 0,
                'offline': 0,
                'unknown': 0,
                'status': 'unknown'
            }

        health = self.device_health
        if health['offline'] > 0:
            status = 'critical'
        elif health['unknown'] > 0:
            status = 'warning'
        else:
            status = 'ok'

    async def async_check_smart_meter(self, sensor_entity_id: str) -> dict:
        state = self.hass.states.get(sensor_entity_id)

        if state is None:
            return {
                'status': 'offline',
                'issue': 'Sensore smart meter non trovato',
                'power_kw': 0.0
            }

        try:
            power_kw = float(state.state)
            return {
                'status': 'ok',
                'power_kw': power_kw,
                'last_updated': state.last_changed.isoformat() if state.last_changed else None
            }
        except (ValueError, TypeError):
            return {
                'status': 'error',
                'issue': f'Valore non valido: {state.state}',
                'power_kw': 0.0
            }

    async def async_get_diagnostics_report(self) -> dict:
        smart_meter = await self.async_check_smart_meter(
            'sensor.quadro_elettrico_primo_piano_smart_meter_potenza_totale'
        )

        return {
            'timestamp': datetime.now().isoformat(),
            'smart_meter': smart_meter,
            'device_health': self.get_device_health_summary(),
            'system_status': smart_meter['status'],
            'recommendations': self._generate_recommendations(smart_meter)
        }

    def _generate_recommendations(self, smart_meter: dict) -> list:
        recommendations = []

        if smart_meter['status'] == 'offline':
            recommendations.append({
                'type': 'critical',
                'message': 'Smart meter offline - Verificare connessione Tuya'
            })
        elif smart_meter['status'] == 'error':
            recommendations.append({
                'type': 'warning',
                'message': 'Smart meter valore non valido - Verificare configurazione'
            })

        if self.device_health and self.device_health['offline'] > 0:
            recommendations.append({
                'type': 'warning',
                'message': f"{self.device_health['offline']} dispositivo/i offline - Verificare connettività"
            })

        return recommendations
