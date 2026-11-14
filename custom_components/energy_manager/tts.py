"""TTS Integration for Energy Manager - Notifiche Vocali."""

import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.service import async_call_from_config

_LOGGER = logging.getLogger(__name__)


class TTSManager:
    """Gestisce le notifiche vocali tramite Qwen3-TTS o Piper."""

    def __init__(self, hass: HomeAssistant, config: dict):
        """Initialize TTS manager."""
        self.hass = hass
        self.config = config
        self.enabled = config.get("tts_enabled", False)
        self.tts_service = config.get("tts_service", "tts.qwen3_say")
        self.media_player = config.get("tts_media_player", "media_player.vlc_telnet")
        self.language = config.get("tts_language", "it")
        self.cache = config.get("tts_cache", True)

    async def async_speak(self, message: str, priority: str = "normal"):
        """Invia annuncio vocale.
        
        Args:
            message: Messaggio da annunciare
            priority: Livello di priorità (normal, high, critical)
        """
        if not self.enabled:
            _LOGGER.debug("TTS disabilitato, salto annuncio: %s", message)
            return

        # Aggiungi prefisso basato sulla priorità
        if priority == "critical":
            message = f"⚠️ Allarme! {message}"
        elif priority == "high":
            message = f"⚡ Attenzione! {message}"
        else:
            message = f"📢 {message}"

        try:
            # Usa il servizio TTS configurato
            await self.hass.services.async_call(
                "tts",
                "google_translate_say",
                {
                    "entity_id": self.media_player,
                    "message": message,
                    "language": self.language,
                    "cache": self.cache
                },
                blocking=False
            )
            _LOGGER.info("TTS annuncio inviato: %s", message)
        except Exception as err:
            _LOGGER.error("Errore TTS: %s", err)

    async def async_speak_power_alert(self, power_kw: float, devices_shed: list):
        """Annuncia alert di potenza eccessiva."""
        devices_str = ", ".join([d.get("name", d.get("entity_id", "")) for d in devices_shed])
        message = (
            f"Il consumo elettrico ha raggiunto {power_kw:.1f} kilowatt. "
            f"Ho spento {devices_str} per rispettare il limite."
        )
        await self.async_speak(message, priority="high")

    async def async_speak_power_restored(self, power_kw: float, devices_restored: list):
        """Annuncia ripristino dispositivi."""
        devices_str = ", ".join([d.get("name", d.get("entity_id", "")) for d in devices_restored])
        message = (
            f"Il consumo è tornato sotto soglia ({power_kw:.1f} kilowatt). "
            f"Ho riacceso {devices_str}."
        )
        await self.async_speak(message, priority="normal")

    async def async_speak_mode_change(self, mode: str):
        """Annuncia cambio modalità."""
        mode_names = {
            "normal": "Normale",
            "vacation": "Vacanza",
            "night": "Notte",
            "solar": "Fotovoltaico",
            "emergenza": "Emergenza"
        }
        mode_name = mode_names.get(mode, mode)
        message = f"Modalità Energy Manager cambiata in {mode_name}."
        await self.async_speak(message, priority="normal")

    async def async_speak_device_offline(self, device_name: str):
        """Annuncia dispositivo offline."""
        message = f"Attenzione: {device_name} non è raggiungibile."
        await self.async_speak(message, priority="critical")

    async def async_speak_daily_summary(self, stats: dict):
        """Annuncia riepilogo giornaliero."""
        message = (
            f"Riepilogo giornaliero Energy Manager: "
            f"{stats.get('total_interventions', 0)} interventi, "
            f"{stats.get('energy_saved_kwh', 0):.1f} kilowattora risparmiati."
        )
        await self.async_speak(message, priority="normal")
