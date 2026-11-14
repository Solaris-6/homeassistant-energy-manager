"""Integrazione con il progetto Yuki."""

import logging
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class YukiIntegration:
    def __init__(self, hass: HomeAssistant, config: dict):
        self.hass = hass
        self.config = config
        self.enabled = config.get('yuki_enabled', False)
        self.notify_entity = config.get('yuki_notify_entity', 'notify.mobile_app_2410fpcc5g')

    async def async_notify_power_alert(self, power_kw: float, devices_shed: list):
        devices_str = ', '.join([d.get('name', d.get('entity_id', '')) for d in devices_shed])
        message = (
            f"⚡ Energy Manager - Potenza eccessiva: {power_kw:.1f} kW\n"
            f"Dispositivi spenti: {devices_str}"
        )
        await self.async_send_notification(message, priority='high')

    async def async_notify_power_restored(self, power_kw: float, devices_restored: list):
        devices_str = ', '.join([d.get('name', d.get('entity_id', '')) for d in devices_restored])
        message = (
            f"✅ Energy Manager - Potenza sotto soglia: {power_kw:.1f} kW\n"
            f"Dispositivi riaccesi: {devices_str}"
        )
        await self.async_send_notification(message, priority='normal')

    async def async_notify_mode_change(self, mode: str):
        mode_names = {
            'normal': 'Normale',
            'vacation': 'Vacanza',
            'night': 'Notte',
            'solar': 'Fotovoltaico',
            'emergenza': 'Emergenza'
        }
        mode_name = mode_names.get(mode, mode)
        message = f"🔄 Energy Manager - Modalità cambiata: {mode_name}"
        await self.async_send_notification(message, priority='normal')

    async def async_notify_daily_summary(self, stats: dict):
        message = (
            f"📊 Energy Manager - Riepilogo Giornaliero\n"
            f"Interventi: {stats.get('total_interventions', 0)}\n"
            f"Energia risparmiata: {stats.get('energy_saved_kwh', 0):.2f} kWh"
        )
        await self.async_send_notification(message, priority='normal')

    async def async_send_notification(self, message: str, priority: str = 'normal'):
        if not self.enabled:
            _LOGGER.debug("Yuki notifiche disabilitate")
            return

        data = {
            'message': message,
            'title': 'Energy Manager'
        }

        if priority == 'high':
            data['data'] = {'importance': 'high', 'channel': 'energia'}
        elif priority == 'critical':
            data['data'] = {'importance': 'high', 'channel': 'allarme'}

        try:
            await self.hass.services.async_call(
                'notify',
                self.notify_entity.split('.')[0] if '.' in self.notify_entity else 'notify',
                data,
                blocking=False
            )
        except Exception as err:
            _LOGGER.error("Errore notifica Yuki: %s", err)
