"""Statistiche Energia per Energy Manager."""

import logging
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

class StatisticsManager:
    def __init__(self, hass: HomeAssistant, config: dict):
        self.hass = hass
        self.config = config
        self.daily_stats = {}
        self.monthly_stats = {}
    async def async_record_intervention(self, action: str, devices: list, power_kw: float):
        self.interventions.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'devices': devices,
            'power_kw': power_kw
        })

    def get_daily_stats(self, date: str = None) -> dict:
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')

        daily_interventions = [
            i for i in self.interventions
            if i['timestamp'].startswith(date)
        ]

        return {
            'date': date,
            'total_interventions': len(daily_interventions),
            'interventions': daily_interventions,
            'energy_saved_kwh': sum(i.get('power_kw', 0) for i in daily_interventions)
        }

    def get_monthly_stats(self, year_month: str = None) -> dict:
        if year_month is None:
            year_month = datetime.now().strftime('%Y-%m')

        monthly_interventions = [
            i for i in self.interventions
            if i['timestamp'].startswith(year_month)
        ]

        return {
            'year_month': year_month,
            'total_interventions': len(monthly_interventions),
            'interventions': monthly_interventions,
            'energy_saved_kwh': sum(i.get('power_kw', 0) for i in monthly_interventions),
    def get_summary(self) -> dict:
        return {
            'total_interventions': len(self.interventions),
            'total_devices_shed': sum(len(i.get('devices', [])) for i in self.interventions),
            'total_energy_saved_kwh': sum(i.get('power_kw', 0) for i in self.interventions),
            'last_intervention': self.interventions[-1] if self.interventions else None
        }

