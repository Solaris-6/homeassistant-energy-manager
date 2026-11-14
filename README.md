# 🏠 Energy Manager - Fase 3: Dashboard Lovelace

## 📋 Struttura File Fase 3

```
custom_components/energy_manager/
├── __init__.py
├── manifest.json
├── const.py
├── config_flow.py
├── sensor.py
├── coordinator.py
├── engine.py
├── storage.py
├── services.yaml
├── dashboard/
│   └── energy_manager_dashboard.yaml
├── translations/
│   ├── it.json
│   └── en.json
└── README.md
```

## 📥 Installazione Dashboard

### Passo 1: Copiare i File sul Raspberry Pi

Tutti i file devono essere copiati da `Z:\custom_components\energy_manager\` alla cartella `config/custom_components/` del Raspberry Pi.

### Passo 2: Aggiungere la Dashboard a Home Assistant

La dashboard Lovelace si trova nel file `dashboard/energy_manager_dashboard.yaml`.

**Opzione A - Tramite File Editor:**
1. Apri Home Assistant → Impostazioni → Pannelli di Controllo → Pannelli
2. Clicca su "Aggiungi Pannello"
3. Scegli "Manuale" (Manual)
4. Incolla il contenuto di `dashboard/energy_manager_dashboard.yaml`

**Opzione B - Tramite configurazione YAML:**
Aggiungi a `configuration.yaml`:

```yaml
panel_custom:
  - name: energy-manager-dashboard
    title: "Energy Manager"
    icon: mdi:lightning-bolt
    sidebar: true
    filename: energy_manager_dashboard.html
```

**Opzione C - Usando le Cards singolarmente:**
Puoi aggiungere le singole cards ai tuoi pannelli esistenti copiandole dal file `dashboard/energy_manager_dashboard.yaml`.

## 🎛️ Caratteristiche della Dashboard

### 📊 Dashboard Principale (`/energy_manager`)

1. **Stato Sistema Energetico**
   - Potenza attuale (kW)
   - Stato del sistema (Normale/Attenzione/Critico)
   - Soglia configurata
   - Ultima azione eseguita

2. **Gauge Potenza Istantanea**
   - Visualizzazione a quadrante
   - Colori: Verde (< 2.5 kW), Giallo (2.5-3.0 kW), Rosso (> 3.0 kW)

3. **Dispositivi Gestiti**
   - Stato di ogni dispositivo (Acceso/Spento)
   - Priorità visualizzata
   - Icone specifiche per ogni dispositivo

4. **Storico Consumo**
   - Grafico storico 24 ore
   - Potenza istantanea e energia totale

5. **Azioni Rapide**
   - Shedding Manuale
   - Modalità Emergenza
   - Modalità Vacanza

6. **Informazioni**
   - Regole di gestione
   - Tabella priorità dispositivi

### 📋 Log Eventi (`/energy_log`)

1. **Storico Attività Dispositivi**
   - Grafico 48 ore
   - Stato di ogni dispositivo nel tempo

2. **Ultimi Eventi**
   - Ultima azione eseguita
   - Totale dispositivi gestiti

## 🔧 Servizi Disponibili

| Servizio | Descrizione | Parametri |
|----------|-------------|-----------|
| `energy_manager.shed_load` | Spegne dispositivi non critici | `devices`, `power_limit` |
| `energy_manager.set_mode` | Cambia modalità operativa | `mode` (normal/vacation/night/solar/emergenza), `threshold_kW` |
| `energy_manager.restore_all` | Riaccende tutti i dispositivi | Nessuno |

### Esempio di chiamata servizio:

```yaml
service: energy_manager.shed_load
data:
  power_limit: 2.5
```

```yaml
service: energy_manager.set_mode
data:
  mode: vacation
  threshold_kW: 2.0
```

## 📊 Priorità Dispositivi

| Priorità | Dispositivo | Consumo Indicativo |
|----------|-------------|-------------------|
| 100 | Frigorifero | ~700 Wh/anno (Critico - mai spento) |
| 90 | Cucina | ~1000 W |
| 80 | Scaldabagno | 1100 W |
| 70 | Lavastoviglie | 1500 W |
| 60 | Condizionatore | 800-1200 W |
| 60 | Lavatrice | 1500 W |

## ⚙️ Regole di Gestione

1. **Soglia attivazione**: 2.8 kW
2. **Margine di sicurezza**: 0.2 kW (max 3.0 kW)
3. **Isteresi**: 30 secondi
4. **Logica**: Quando potenza > soglia → Spegne dispositivi a bassa priorità (prima i più bassi)
5. **Ripristino**: Quando potenza < soglia → Riaccende dispositivi priorità alta

## ⚠️ Importante

- L'interruttore generale (`switch.quadro_elettrico_primo_piano_sy2_misure_interruttore`) NON viene mai spento
- Il frigorifero (priorità 100) è considerato critico e non viene sganciato
- La dashboard richiede Home Assistant 2023.9 o superiore

## 🐛 Troubleshooting

| Problema | Soluzione |
|----------|-----------|
| Dashboard non appare | Verifica che i file siano nella cartella corretta sul Pi |
| Servizi non trovati | Riavvia Home Assistant dopo l'installazione |
| Sensore non mostra dati | Verifica che `sensor.quadro_elettrico_primo_piano_smart_meter_potenza_totale` esista |
| Dispositivi non si spengono | Verifica che gli entity ID siano corretti |

## 📞 Supporto

Per problemi o suggerimenti, crea un'issue sul repository GitHub del progetto.

---

**Versione**: 0.1.0 - Fase 3  
**Data**: 14/11/2026  
**Autore**: Cline AI Assistant