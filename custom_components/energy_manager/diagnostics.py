"""Diagnostica Avanzata per Energy Manager."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class DiagnosticsManager:
    """Gestisce la diagnostica dei dispositivi e del sistema."""

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any]) -> None:
        self.hass = hass
        self.config = config
        self.device_health: Dict[str, Any] = {}
        self.offline_threshold: int = 300  # Default: 5 minutes

    async def async_check_device_health(self, devices: List[Dict]) -> Dict[str, Any]:
        """Check health of all configured devices."""
        health_report: Dict[str, Any] = {
            'timestamp': datetime.now().isoformat(),
            'total_devices': len(devices),
            'online': 0,
            'offline': 0,
            'unknown': 0,
            'devices': []
        }

        for device in devices:
            entity_id = device.get('entity_id')
            device_name = device.get('name', str(entity_id)) if entity_id else ''

            if not entity_id or not isinstance(entity_id, str):
                health_report['devices'].append({
                    'entity_id': None,
                    'name': device_name,
                    'status': 'unknown',
                    'last_seen': None,
                    'issue': 'Entity ID non configurato'
                })
                health_report['unknown'] += 1
                continue

            state = self.hass.states.get(entity_id) if hasattr(self.hass, 'states') else None

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

            last_changed = state.last_changed if hasattr(state, 'last_changed') else None
            
            if last_changed:
                try:
                    time_since = datetime.now() - last_changed.replace(tzinfo=None) if isinstance(last_changed, datetime) else timedelta(0)
                    if time_since > timedelta(seconds=self.offline_threshold):
                        health_report['devices'].append({
                            'entity_id': entity_id,
                            'name': device_name,
                            'status': 'offline',
                            'last_seen': last_changed.isoformat() if hasattr(last_changed, 'isoformat') else str(last_changed),
                            'issue': f'Nessun aggiornamento da {int(time_since.total_seconds())} secondi'
                        })
                        health_report['offline'] += 1
                        continue
                except (AttributeError, TypeError):
                    pass

            # Device is online
            health_report['devices'].append({
                'entity_id': entity_id,
                'name': device_name,
                'status': state.state if hasattr(state, 'state') else 'unknown',
                'last_seen': last_changed.isoformat() if (hasattr(last_changed, 'isoformat') and last_changed) else None,
                'issue': None
            })
            health_report['online'] += 1

        self.last_check = datetime.now() if hasattr(self, 'last_check') else datetime.now()
        self.device_health = health_report
        return health_report

    def get_device_health_summary(self) -> Dict[str, Any]:
        """Return a summary of device health."""
        if not self.device_health or not isinstance(self.device_health, dict):
            return {
                'total_devices': 0,
                'online': 0,
                'offline': 0,
                'unknown': 0,
                'status': 'unknown'
            }

        health = self.device_health
        
        if isinstance(health.get('offline'), (int, float)) and health['offline'] > 0:
            status = 'critical'
        elif isinstance(health.get('unknown'), (int, float)) and health['unknown'] > 0:
            status = 'warning'
        else:
            status = 'ok'

        return {
            'total_devices': health.get('total_devices', 0),
            'online': health.get('online', 0),
            'offline': health.get('offline', 0),
            'unknown': health.get('unknown', 0),
            'status': status
        }

    async def async_check_smart_meter(self, sensor_entity_id: str) -> Dict[str, Any]:
        """Check smart meter state."""
        if not sensor_entity_id or not isinstance(sensor_entity_id, str):
            return {
                'status': 'error',
                'issue': 'Entity ID non valido'
            }

        state = self.hass.states.get(sensor_entity_id) if hasattr(self.hass, 'states') else None

        if state is None:
            return {
                'status': 'offline',
                'issue': 'Sensore smart meter non trovato',
                'power_kw': 0.0
            }

        try:
            power_kw = float(state.state) if hasattr(state, 'state') else 0.0
            last_updated = state.last_changed.isoformat() if (hasattr(state, 'last_changed') and state.last_changed) else None
            
            return {
                'status': 'ok',
                'power_kw': power_kw,
                'last_updated': last_updated
            }
        except (ValueError, TypeError):
            return {
                'status': 'error',
                'issue': f'Valore non valido: {state.state if hasattr(state, "state") else state}',
                'power_kw': 0.0
            }

    async def async_get_diagnostics_report(self) -> Dict[str, Any]:
        """Generate a comprehensive diagnostics report."""
        smart_meter = await self.async_check_smart_meter(
            'sensor.quadro_elettrico_primo_piano_smart_meter_potenza_totale'
        )

        # Get device health summary
        health_summary = self.get_device_health_summary()

        return {
            'timestamp': datetime.now().isoformat(),
            'smart_meter': smart_meter,
            'device_health': health_summary,
            'system_status': smart_meter['status'],
            'recommendations': self._generate_recommendations(smart_meter)
        }

    def _generate_recommendations(self, smart_meter: Dict[str, Any]) -> List[Dict]:
        """Generate recommendations based on diagnostics."""
        recommendations: List[Dict] = []

        if not isinstance(smart_meter, dict):
            return recommendations

        status = smart_meter.get('status', 'unknown')

        if status == 'offline':
            recommendations.append({
                'type': 'critical',
                'message': 'Smart meter offline - Verificare connessione Tuya'
            })
        elif status == 'error':
            recommendations.append({
                'type': 'warning',
                'message': 'Smart meter valore non valido - Verificare configurazione'
            })

        if isinstance(health_summary, dict) and health_summary.get('offline', 0) > 0:
            offline_count = health_summary['offline']
            recommendations.append({
                'type': 'warning',
                'message': f'{offline_count} dispositivo/i offline - Verificare connettività'
            })

        return recommendations
