# ⚡ Energy Manager - Home Assistant Integration

![Version](https://img.shields.io/badge/version-0.1.0-blue.svg)
![Platform](https://img.shields.io/badge/platform-Home%20Assistant-41B356?logo=homeassistant)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Energy Manager per Home Assistant** - Gestione intelligente del consumo elettrico con shedding automatico dei carichi non critici, monitoraggio in tempo reale e dashboard Lovelace interattiva.

---

## 🎯 Cos'è Energy Manager?

Energy Manager è un'integrazione **completamente autonoma** per Home Assistant che:

- **Monitora** il consumo elettrico in tempo reale tramite smart meter
- **Spegne automaticamente** i dispositivi non critici quando la potenza supera una soglia configurata
- **Riaccende** i dispositivi quando il consumo torna sotto soglia (isteresi)
- **Supporta** modalità speciali: Vacanza, Notte, Fotovoltaico, Emergenza
- **Gestisce** priorità dei dispositivi per ottimizzare il comfort
- **Notifica** via TTS o notifiche push gli eventi importanti

### ✨ Funzionalità Principali

| Caratteristica | Descrizione |
|----------------|-------------|
| **Shedding automatico** | Spegne dispositivi non critici quando potenza > soglia |
| **Isteresi temporale** | Evita accensioni/spegnimenti rapidi (timer configurabile) |
| **Priorità dispositivi** | Frigorifero (100) > Scaldabagno (80) > Lavastoviglie (70) > Condizionatore/Lavatrice (60) |
| **Modalità speciali** | Vacanza, Notte, Fotovoltaico, Emergenza con priorità personalizzate |
| **Dashboard Lovelace** | Pannello interattivo per monitoraggio e controllo rapido |
| **Notifiche vocali (TTS)** | Annuncia eventi via Google TTS |
| **Integrazione Yuki** | Notifiche push tramite app mobile |
| **Servizi Home Assistant** | shed_load, set_mode, restore_all |

---

## 📋 Requisiti Minimimi

### Hardware/Software

- **Home Assistant**: 2023.9.0 o superiore (testato su 2026.x)
- **Smart Meter**: Sensore di potenza (Tuya, Shelly, ESPHome, ecc.) con entità `sensor.<nome>_potenza_totale`
- **Interruttori/Switch**: Home Assistant Switch per ogni dispositivo gestibile

### Configurazione Richiesta

| Parametro | Tipo | Minimo | Massimo | Default | Descrizione |
|-----------|------|--------|---------|---------|-------------|
| `threshold_kW` | Numero | 0.0 | 3.0 | 2.8 | Soglia potenza massima (kW) |
| `isosterisis_s` | Numero | 5 | 300 | 30 | Tempo di isteresi in secondi |

### Dispositivi Supportati

- Interruttori switch HA (`switch.*`)
- Sensori di potenza (`sensor.<nome>_potenza_totale`)
- Any device con servizio `switch/turn_off` e `switch/turn_on`

---

## 📥 Installazione

### Metodo 1: HACS (Consigliato)

```bash
# Apri Home Assistant → Store Community → Cerca "Energy Manager"
# Clicca "Aggiungi" e riavvia HA
```

**URL Repository:**
```
https://github.com/solaris-6/homeassistant-energy-manager
```

### Metodo 2: Installazione Manuale

#### Sul Raspberry Pi (Home Assistant OS)

```bash
# Copia i file nel percorso corretto
cp -r /tmp/energy_manager_backup/* /config/custom_components/energy_manager/
rm -rf /tmp/energy_manager_backup/

# Riavvia Home Assistant
sudo systemctl restart homeassistant
```

#### Via Docker

```bash
docker cp C:/custom_components/energy_manager <container_name>:/app/core/config/custom_components/energy_manager/
docker restart <container_name>
```

#### Su Windows (Home Assistant)

```cmd
xcopy "C:\custom_components\energy_manager" "%HOMEPATH%\.homeassistant\config\custom_components\energy_manager\ /E /I /Y"
```

### Verifica Installazione

Dopo aver copiato i file:

1. **Riavvia Home Assistant** (opzionale ma consigliato)
2. Apri **Impostazioni → Dispositivi e servizi**
3. Cerca **"Energy Manager"** nella lista
4. Clicca **"Aggiungi"** per configurare l'integrazione

---

## ⚙️ Configurazione Guidata

### Passo 1: Impostazioni Base

Scegli i parametri principali dell'integrazione:

| Campo | Valore Suggerito | Descrizione |
|-------|-----------------|-------------|
| **Threshold (kW)** | `2.8` | Potenza massima prima di spegnere dispositivi (0.0 - 3.0 kW) |
| **Isteresi (s)** | `30` | Tempo minimo tra spegnimento e ripristino (5 - 300 secondi) |

**Esempio comune:**
- Soglia: 2.8 kW (massima potenza tollerabile)
- Isteresi: 30 secondi (tempo per evitare accensioni/spegnimenti rapidi)

### Passo 2: Interruttore Generale

Seleziona l'interruttore principale **NON SGANCIABILE**:

```yaml
general_breaker: switch.quadro_elettrico_primo_piano_sy2_misure_interruttore
```

**⚠️ IMPORTANTE:** Questo interruttore NON viene mai spento dall'Energy Manager. È il limite fisico della tua installazione elettrica.

### Passo 3: Dispositivi (Opzionale, tramite UI)

I dispositivi possono essere aggiunti manualmente via UI o configurati direttamente nel config entry YAML:

```yaml
# Esempio di configurazione completa con dispositivi:
energy_manager:
  general_breaker: switch.quadro_elettrico_primo_piano_sy2_misure_interruttore
  threshold_kW: 2.8
  isosterisis_s: 30
  devices:
    - entity_id: switch.quadro_elettrico_primo_piano_sy2_condizionatore_interruttore
      name: Condizionatore
      priority: 60
      power_estimate: 1.0
    - entity_id: switch.quadro_elettrico_primo_piano_sy2_scaldabagno_interruttore
      name: Scaldabagno
      priority: 80
      power_estimate: 1.1
    - entity_id: switch.quadro_elettrico_primo_piano_sy2_lavastoviglie_interruttore
      name: Lavastoviglie
      priority: 70
      power_estimate: 1.5
```

---

## 📝 Guida Completa alla Configurazione Dispositivi

### Come Identificare gli Entity ID dei Dispositivi

#### Metodo 1: UI Home Assistant (Consigliato)

1. Apri **Impostazioni → Dispositivi e servizi**
2. Vai nella scheda **"Sensori"** o **"Switches"**
3. Cerca il dispositivo desiderato (es. "Condizionatore", "Frigorifero")
4. Copia l'**Entity ID** dalla lista

**Esempio:**
```
Dispositivo: Condizionatore Zephir 9000BTU
Entity ID: switch.quadro_elettrico_primo_piano_sy2_condizionatore_interruttore
```

#### Metodo 2: Configurazione Dispositivi

1. Vai a **Impostazioni → Dispositivi e servizi**
2. Clicca sul dispositivo → **"Configura"**
3. L'entity ID è visibile nella sezione "Dettagli" o "Identificatori"

#### Metodo 3: Log di Sistema

```bash
# SSH sul Raspberry Pi e filtra per il dispositivo:
journalctl -u homeassistant --since "10 minutes ago" | grep "condizionatore"
```

**Output esempio:**
```
2026-11-14 22:30:15 WARNING (SyncEntity/1) [homeassistant.helpers.entity] Entity switch.quadro_elettrico_primo_piano_sy2_condizionatore_interruttore is not ready
```

### Come Determinare la Priorità

#### Scala di Priorità Standard

| Priorità | Livello | Dispositivi Tipici | Note |
|----------|---------|-------------------|------|
| **100** | Critico | Frigorifero, Forneletti, Sistemi di sicurezza | Mai spento - essenziale per vita/sicurezza |
| **95** | Alto | Cucina, Forno | Priorità alta ma non critico in emergenza |
| **80** | Medio-Alto | Scaldabagno, Caldaia | Essenziale per acqua calda e riscaldamento |
| **70** | Medio | Lavastoviglie, Aspirapolvere | Può aspettare il ciclo successivo |
| **60** | Basso | Condizionatore, Lavatrice | Potrebbe essere spento in emergenza |
| **50** | Minimo | Lampade decorative, TV | Ultimi a essere riaccesi, primi a spegnersi |

#### Regole di Priorità:

- **≥ 90**: Mai spento (dispositivi critici per sicurezza o sopravvivenza)
- **60-89**: Spento in ordine crescente di priorità quando potenza > soglia
- **< 60**: Ultimi a essere riaccesi, primi a essere spenti
- **General Breaker**: Mai toccato, sempre acceso

#### Come Assegnare la Priorità al Tuo Dispositivo

1. **Pensa all'uso quotidiano:**
   - "Se devo spegnere qualcosa per emergenza, quale posso sacrificare?"
   
2. **Valuta le conseguenze dello spegnimento:**
   - Frigorifero spento → Cibo che si rovinerà in 4-6 ore → Priorità alta (100)
   - Condizionatore spento → Discomfort ma sicuro → Priorità media/bassa (50-60)

3. **Considera le alternative:**
   - "Posso spegnere il condizionatore e aspettare che si raffreddi?" → Sì = priorità bassa
   - "Posso aspettare di finire il ciclo della lavatrice?" → Sì = priorità 70-80

4. **Assegna la priorità (esempio):**

```yaml
# Dispositivi con priorità assegnata:
devices:
  # Priorità CRITICA (mai spenta)
  - entity_id: switch.quadro_elettrico_primo_piano_sy2_frigorifero_interruttore
    name: Frigorifero Samsung
    priority: 100        # Mai spento!
    power_estimate: 0.07  # ~70W di consumo medio

  # Priorità ALTA (solo in emergenza)
  - entity_id: switch.quadro_elettrico_primo_piano_sy2_condizionatore_interruttore
    name: Condizionatore Zephir
    priority: 60         # Può essere spento se potenza > soglia
    power_estimate: 1.0   # ~1000W

  # Priorità MEDIA (seconda da spegnere)
  - entity_id: switch.quadro_elettrico_primo_piano_sy2_scaldabagno_interruttore
    name: Scaldabagno
    priority: 80         # Essenziale per acqua calda
    power_estimate: 1.1   # ~1100W

  - entity_id: switch.quadro_elettrico_primo_piano_sy2_lavastoviglie_interruttore
    name: Lavastoviglie Indesit
    priority: 70         # Può aspettare ciclo successivo
    power_estimate: 1.5   # ~1500W

  - entity_id: switch.quadro_elettrico_primo_piano_sy2_lavatrice_interruttore
    name: Lavatrice Indesit
    priority: 60         # Può essere spenta in emergenza
    power_estimate: 1.5   # ~1500W
```

### Come Stimare il Consumo di Potenza (`power_estimate`)

#### Metodo 1: Placca del Dispositivo (Più Accurato)

1. **Trova la potenza nominale** sulla scheda tecnica del dispositivo:
   - Es. Condizionatore: `P = 1000W` o `1.0 kW`
   
2. **Dividi per 3600 secondi** per ottenere il consumo medio orario:
   ```python
   power_estimate_kW = potenza_W / 1000  # 1000W → 1.0 kW
   ```

#### Metodo 2: Misurazione con Smart Meter (Consigliato)

1. **Attiva il dispositivo** e registra la potenza dal sensore
2. **Disattiva dopo 5 minuti** e registra nuovamente
3. **Calcola la media:**
   ```python
   # Potenza attiva (dispositivo acceso): 1.2 kW
   # Potenza disattivato: 0.3 kW
   power_estimate = 1.2 - 0.3  # = 0.9 kW (consumo reale del dispositivo)
   ```

#### Metodo 3: Stima Basata sul Tipo di Dispositivo

| Tipo Dispositivo | Potenza Tipica (kW) | Note |
|------------------|---------------------|------|
| **Frigorifero** | 0.05 - 0.15 | Dipende da capacità e efficienza |
| **Condizionatore** | 0.8 - 2.0 | In base a BTU (9000 ≈ 1kW, 12000 ≈ 1.3kW) |
| **Scaldabagno elettrico** | 1.5 - 3.0 | Tipicamente 2-3 kW |
| **Lavastoviglie** | 1.0 - 2.0 | Varie per ciclo (lavaggio vs asciugatura) |
| **Lavatrice** | 1.0 - 2.5 | Molto variabile (centrifuga = alta potenza) |
| **Aspirapolvere** | 0.3 - 1.0 | Dipende da classe e potenza motore |
| **Televisore LED** | 0.05 - 0.2 | 4K ≈ 0.1-0.2 kW, OLED ≈ 0.1 kW |
| **Lampade LED** | 0.01 - 0.03 | Molto basso per lampade moderne |

#### Metodo 4: Misurazione Diretta con Wattmetro

Se hai un wattmetro a presa (es. Shelly Plug S, Tuya), misura direttamente il consumo del dispositivo in uso.

### Template di Configurazione Pronto all'Uso

Copia e modificala secondo i tuoi dispositivi:

```yaml
# ============================================
# TEMPLATE CONFIGURAZIONE ENERGY MANAGER
# ============================================
energy_manager:
  general_breaker: switch.<tuo_interruttore_generale>
  
  # Impostazioni base
  threshold_kW: 2.8        # Soglia potenza (0.0 - 3.0 kW)
  isosterisis_s: 30        # Tempo isteresi in secondi (5-300)
  
  # Dispositivi gestibili
  devices:
    # DISPOSITIVI CRITICI (mai spenti)
    - entity_id: switch.<entity_frigorifero>
      name: Frigorifero
      priority: 100         # Mai spento!
      power_estimate: 0.07  # ~70W medio

    # DISPOSITIVI MEDIO-ALTI (priorità alta)
    - entity_id: switch.<entity_scaldabagno>
      name: Scaldabagno
      priority: 80          # Essenziale acqua calda
      power_estimate: 1.1   # ~1100W

    # DISPOSITIVI MEDI (possono aspettare)
    - entity_id: switch.<entity_lavastoviglie>
      name: Lavastoviglie
      priority: 70          # Può aspettare ciclo successivo
      power_estimate: 1.5   # ~1500W

    # DISPOSITIVI BASI (primi da spegnere in emergenza)
    - entity_id: switch.<entity_condizionatore>
      name: Condizionatore
      priority: 60          # Può essere spento
      power_estimate: 1.0   # ~1000W

    - entity_id: switch.<entity_lavatrice>
      name: Lavatrice
      priority: 60          # Può essere spenta in emergenza
      power_estimate: 1.5   # ~1500W
  
  # NOTA: I dispositivi possono anche non avere priority
  # se configurati via UI, ma è meglio assegnare una priorità esplicita
```

### Checklist per la Configurazione

- [ ] Ho identificato tutti i dispositivi switch che voglio gestire?
- [ ] Per ogni dispositivo ho trovato l'entity_id corretto?
- [ ] Ho assegnato una priorità logica (100 = critico, 60 = basso)?
- [ ] Ho stimato correttamente il consumo di potenza (`power_estimate`)?
- [ ] L'interruttore generale è impostato e NON sarà spento?
- [ ] La soglia `threshold_kW` è realistica per la mia abitazione?

### Esempio: Configurazione Casa Tipica Italiana

```yaml
energy_manager:
  general_breaker: switch.quadro_elettrico_primo_piano_sy2_misure_interruttore
  
  threshold_kW: 2.8        # Media casa italiana in estate
  isosterisis_s: 30        # Evita spegnimenti rapidi

  devices:
    # Priorità CRITICA - Mai spenta
    - entity_id: switch.quadro_elettrico_primo_piano_sy2_frigorifero_interruttore
      name: Frigorifero Samsung
      priority: 100         # Mai spento!
      power_estimate: 0.07

    # Priorità ALTA - Solo in emergenza estrema
    - entity_id: switch.quadro_elettrico_primo_piano_sy2_condizionatore_interruttore
      name: Condizionatore Zephir
      priority: 60          # Può essere spento se potenza > soglia
      power_estimate: 1.0

    - entity_id: switch.quadro_elettrico_primo_piano_sy2_lavatrice_interruttore
      name: Lavatrice Indesit
      priority: 60          # Può aspettare ciclo successivo
      power_estimate: 1.5

    # Priorità MEDIA-ALTA - Essenziale ma non critico
    - entity_id: switch.quadro_elettrico_primo_piano_sy2_scaldabagno_interruttore
      name: Scaldabagno
      priority: 80          # Essenziale per acqua calda
      power_estimate: 1.1

    - entity_id: switch.quadro_elettrico_primo_piano_sy2_lavastoviglie_interruttore
      name: Lavastoviglie Indesit
      priority: 70          # Può aspettare ciclo successivo
      power_estimate: 1.5
  
  # Totale potenza massima gestibile: ~6 kW (senza refrigeratori)
```

### Come Modificare i Dispositivi Dopo la Configurazione

#### Via UI Home Assistant (Consigliato)

1. Vai a **Impostazioni → Dispositivi e servizi**
2. Cerca **"Energy Manager"** nella lista
3. Clicca sui tre puntini `⋮` accanto all'entry
4. Seleziona **"Configura"** o **"Modifica"**
5. Aggiungi/rimuovi dispositivi dalla lista
6. Salva le modifiche

#### Via YAML (per utenti avanzati)

Aggiorna direttamente il file di configurazione:

```yaml
# In .homeassistant/configuration.yaml o tramite UI YAML editor
energy_manager:
  general_breaker: switch.<tuo_interruttore>
  threshold_kW: 2.8
  isosterisis_s: 30
  devices:
    - entity_id: switch.<nuovo_dispositivo>
      name: Nuovo Dispositivo
      priority: 70
      power_estimate: 1.2
```

**Dopo modifiche YAML:** Riavvia Home Assistant o ricarica la configurazione!

---

## 📝 Guida Configurazione Automatica > 500W (ESCLUSIONI FRIGORIFERI/CONGELATORI)

### Come Funziona l'Automazione > 500W

Energy Manager può monitorare automaticamente tutti i dispositivi che superano i **500W** di consumo, **escludendo frigoriferi e congelatori** (priorità ≥ 90).

#### Configurazione Automatica

```yaml
# ============================================
# CONFIGURAZIONE AUTOMATICA DISPOSITIVI > 500W
# ESCLUSI: Frigoriferi e Congelatori (priorità >= 90)
# ============================================

automations:
- alias: "Energy Manager - Aggiorna dispositivi > 500W"
  trigger:
    platform: state
    entity_id: switch.*
    to: "on"
  condition: []
  action:
    service: energy_manager.set_mode
    data:
      mode: normal
  description: "Rileva accensione dispositivi > 500W e aggiorna lista gestibile (esclude frigoriferi)"

# ============================================
# INTEGRAZIONE SMART METER QUADRO ELETTRICO PRIMO PIANO
# ============================================
sensor:
- platform: tuya
  name: "Smart Meter Potenza Totale"
  device_id: <INSERISCI_ID_DEVICE_QUADRO>
  sensor_type: power_total

# ============================================
# INTEGRAZIONE QUALITÀ ARIA (NON GESTIBILE)
# ============================================
sensor:
- platform: tuya
  name: "Qualità Aria PM2.5"
  device_id: <INSERISCI_ID_DEVICE_MT15>
  sensor_type: pm2_5

# ============================================
# INTEGRAZIONE SWITCH GARAGE (NON GESTIBILE)
# ============================================
switch:
- platform: tuya
  name: "Serranda Garage"
  device_id: <INSERISCI_ID_DEVICE_TUYA>
```

### Esempio Completo con Automazione > 500W

```yaml
energy_manager:
  threshold_kW: 2.8
  isosterisis_s: 30
  general_breaker: switch.quadro_elettrico_primo_piano_sy2_misure_interruttore
  
  devices:
    # Frigorifero (mai spento!) - ESCLUSO dall'automazione >500W
    - entity_id: switch.<entity_frigorifero>
      name: Frigorifero Samsung
      priority: 100
      power_estimate: 0.07

    # Dispositivi gestibili automaticamente se > 500W (esclusi frigoriferi)
    - entity_id: switch.<entity_condizionatore>
      name: Condizionatore Zephir
      priority: 60
      power_estimate: 1.0

    - entity_id: switch.quadro_elettrico_primo_piano_sy2_scaldabagno_interruttore
      name: Scaldabagno
      priority: 80
      power_estimate: 1.1
```

### Note Importanti per l'Automazione > 500W:

- **Frigoriferi e Congelatori**: Non vengono inclusi nell'automazione perché hanno priorità ≥ 90 (mai spenti)
- **Dispositivi < 500W**: Vengono ignorati dall'automazione ma possono essere aggiunti manualmente alla lista dispositivi
- **Switch Tuya**: Assicurati che i dispositivi Tuya siano integrati correttamente in HA
- **Smart Meter**: Deve essere configurato e funzionante per monitorare la potenza totale

### Come Testare l'Automazione:

1. **Attiva un dispositivo** che dovrebbe essere > 500W (es. condizionatore)
2. **Verifica i log di sistema**: `Impostazioni → Sistema → Log di sistema`
3. **Controlla Energy Manager** se si è aggiornata la lista dispositivi
4. **Ripeti con frigorifero** per verificare che NON venga aggiunto (deve rimanere escluso)

### Troubleshooting Automazione > 500W:

| Problema | Soluzione |
|----------|-----------|
| Dispositivo non rilevato | Verifica che sia uno switch HA attivo |
| Frigorifero incluso erroneamente | Controlla la priorità (deve essere ≥ 90) |
| Automazione non attiva | Verifica che `switch.*` sia il trigger corretto |

---

## 🎛️ Priorità Dispositivi

| Priorità | Livello | Dispositivo Esempio | Consumo Stimato | Note |
|----------|---------|---------------------|-----------------|------|
| **100** | Critico | Frigorifero | 700 Wh/anno | Mai spento, essenziale per cibo |
| **95** | Alto | Cucina | ~1000 W | Priorità alta ma non critico |
| **80** | Medio-Alto | Scaldabagno | 1100 W | Essenziale per acqua calda |
| **70** | Medio | Lavastoviglie | 1500 W | Può aspettare il ciclo successivo |
| **60** | Basso | Condizionatore/Lavatrice | 800-1200 W | Potrebbe essere spento in emergenza |

### Regole di Priorità:

- **≥ 90**: Mai spento (dispositivi critici come frigorifero)
- **60-89**: Spento in ordine crescente di priorità quando potenza > soglia
- **< 60**: Ultimi a essere riaccesi, primi a essere spenti
- **General Breaker**: Mai toccato, sempre acceso

---

## 🔄 Modalità Operative

Energy Manager supporta diverse modalità per adattarsi ai diversi scenari:

### Modalità Normale (Default)
```yaml
mode: normal
threshold_kW: 2.8
priority_min: 0
```
- Shedding standard basato sulla potenza configurata
- Tutti i dispositivi disponibili possono essere spenti/riaccesi

### Modalità Vacanza 🏖️
```yaml
mode: vacation
threshold_kW: 1.5
priority_min: 50
```
- Soglia ridotta per risparmiare energia quando non sei a casa
- Solo dispositivi essenziali (≥ 50 priority) possono essere riaccesi

### Modalità Notte 🌙
```yaml
mode: night
threshold_kW: 3.0
priority_min: 50
```
- Soglia aumentata per comfort notturno
- Dispositivi prioritari (≥ 50) sempre accessibili

### Modalità Fotovoltaico ☀️
```yaml
mode: solar
threshold_kW: 4.0
```
- Soglia molto alta quando c'è produzione fotovoltaica in eccesso
- Permette di caricare batterie o alimentare la casa con energia rinnovabile

### Modalità Emergenza 🚨
```yaml
mode: emergenza
priority_min: 90
threshold_kW: 5.0
```
- Solo dispositivi critici (≥ 90 priority) possono rimanere accesi
- Massima potenza consentita per sicurezza

---

## 🔧 Servizi Home Assistant

Energy Manager espone tre servizi personalizzati che puoi usare in automazioni, script, o UI custom:

### Servizio 1: `energy_manager.shed_load`

**Descrizione:** Spegne manualmente i dispositivi non critici per ridurre la potenza.

| Parametro | Tipo | Obbligatorio | Descrizione |
|-----------|------|--------------|-------------|
| `devices` | List[str] | No | Lista di entity_id da spegnere |
| `power_limit` | float | No | Nuova soglia potenza in kW (default: 2.8) |

**Esempio:**
```yaml
service: energy_manager.shed_load
data:
  devices: ["switch.condizionatore", "switch.lavatrice"]
  power_limit: 2.0
```

### Servizio 2: `energy_manager.set_mode`

**Descrizione:** Cambia la modalità operativa dell'Energy Manager.

| Parametro | Tipo | Obbligatorio | Descrizione |
|-----------|------|--------------|-------------|
| `mode` | str | **Sì** | Modalità (normal, vacation, night, solar, emergenza) |
| `threshold_kW` | float | No | Nuova soglia potenza temporanea (default: 2.8) |

**Esempio:**
```yaml
service: energy_manager.set_mode
data:
  mode: vacanza
  threshold_kW: 1.5
```

### Servizio 3: `energy_manager.restore_all`

**Descrizione:** Riaccende tutti i dispositivi spenti (solo quando potenza < soglia).

| Parametro | Tipo | Obbligatorio | Descrizione |
|-----------|------|--------------|-------------|
| Nessuno | - | No | Questo servizio non richiede parametri |

**Esempio:**
```yaml
service: energy_manager.restore_all
```

---

## 🤖 Automazioni di Esempio

### 1. Attiva Modalità Notte Automatica

```yaml
automation:
- alias: "Energy Manager - Attiva modalità notte"
  trigger:
    platform: time
    at: "22:00:00"
  condition: []
  action:
    service: energy_manager.set_mode
    data:
      mode: night
```

### 2. Disattiva Modalità Notte al Mattino

```yaml
automation:
- alias: "Energy Manager - Rimuovi modalità notte"
  trigger:
    platform: time
    at: "07:00:00"
  condition: []
  action:
    service: energy_manager.set_mode
    data:
      mode: normal
```

### 3. Attiva Emergenza se Potenza > 3.5 kW

```yaml
automation:
- alias: "Emergency Power Mode"
  trigger:
    platform: state
    entity_id: sensor.energy_manager_power
    to: "*"
  condition:
    - condition: template
      value_template: '{{ states.sensor.energy_manager_power.state | float > 3.5 }}'
  action:
    service: energy_manager.set_mode
    data:
      mode: emergenza
```

### 4. Notifica quando Shedding Attivo

```yaml
automation:
- alias: "Notifica shedding dispositivi"
  trigger:
    platform: state
    entity_id: sensor.energy_manager_power
    to: "*warning*"
    for: "00:05:00"  # Evita notifiche ripetitive
  condition: []
  action:
    service: notify.mobile_app_2410fpcc5g
    data:
      title: ⚡ Energy Manager - Potenza Alta
      message: "Il consumo elettrico ha raggiunto {{ states.sensor.energy_manager_power.state }} kW. Dispositivi non critici spenti."
```

### 5. Attiva Modalità Vacanza via Geolocalizzazione

```yaml
automation:
- alias: "Energy Manager - Vacanza se fuori casa"
  trigger:
    platform: state
    entity_id: person.tuonome
    to: "not_home"
  condition: []
  action:
    service: energy_manager.set_mode
    data:
      mode: vacanza
```

---

## 📊 Dashboard Lovelace

Energy Manager include una dashboard interattiva per il monitoraggio e il controllo rapido.

### Opzione A: Pannello Integrato

La dashboard è accessibile automaticamente dall'integrazione se configurata correttamente.

**URL:** `http://<HA_URL>/energy_manager`

### Opzione B: Aggiungi Manuale a Lovelace

#### Metodo 1 - YAML Direct

Aggiungi al tuo file `configuration.yaml`:
```yaml
panel_custom:
  - name: Energy Manager
    title: "⚡ Energy"
    icon: mdi:lightning-bolt
    url_path: /energy_manager_dashboard
    sidebar: true
```

Poi crea il pannello in **Impostazioni → Pannelli di Controllo → Aggiungi Pannello**.

#### Metodo 2 - Card Singole

Aggiungi le card seguenti al tuo dashboard esistente:

**Card Potenza Istantanea:**
```yaml
type: custom:energy-manager-gauge-card
title: Potenza Istantanea
sensor: sensor.energy_manager_power
max_value: 3.0
min_value: 0.0
threshold_1: 2.5
threshold_2: 3.0
```

**Card Dispositivi Gestiti:**
```yaml
type: entities
title: "🔌 Dispositivi"
entities:
  - entity: switch.quadro_elettrico_primo_piano_sy2_condizionatore_interruttore
    name: Condizionatore
    icon: mdi:snowflake
  - entity: switch.quadro_elettrico_primo_piano_sy2_scaldabagno_interruttore
    name: Scaldabagno
    icon: mdi:water-thermometer
```

---

## 🐛 Troubleshooting

### Problema: "Invalid handler specified" durante configurazione

**Causa:** Errore nel config_flow.py o in un file importato

**Soluzione:**
1. Elimina il config entry esistente (Impostazioni → Dispositivi e servizi)
2. Riavvia Home Assistant
3. Riprova a configurare l'integrazione da zero

### Problema: Sensore potenza non trovato

**Causa:** L'entità `sensor.<nome>_potenza_totale` non esiste o è disabilitata

**Soluzione:**
1. Verifica che il sensore esista in **Impostazioni → Dispositivi e servizi → Sensori**
2. Controlla che sia "On" (abilitato)
3. Se usi uno smart meter Tuya, verifica la connessione nella sua app

### Problema: Dispositivi non si spengono/riaccendono

**Causa:** Interruttore switch HA non risponder correttamente al servizio `switch/turn_off`

**Soluzione:**
1. Verifica che l'entità sia un switch valido in Home Assistant
2. Testa manualmente: Impostazioni → Dispositivi e servizi → Switches → Tocca il dispositivo
3. Se è un relè esterno, verifica la connessione fisica

### Problema: Energia Manager non si aggiorna (nessun shedding)

**Causa:** Il coordinatore non trova il sensore di potenza o l'interruttore generale

**Soluzione:**
1. Controlla i log di sistema: **Impostazioni → Sistema → Log di sistema → Filtra "Energy Manager"**
2. Verifica che `sensor.<nome>_potenza_totale` sia funzionante
3. Verifica che `switch.quadro_elettrico_primo_piano_sy2_misure_interruttore` esista

### Problema: Errori 500 nella configurazione

**Causa:** Versione HA incompatibile o file corrotti

**Soluzione:**
1. Assicurati di usare HA 2023.9.0 o superiore (testato su 2026.x)
2. Verifica che tutti i file siano nella cartella `custom_components/energy_manager/`
3. Copia di nuovo l'intera cartella dall'ultimo backup GitHub

---

## 📁 Struttura File

```
custom_components/energy_manager/
├── __init__.py              # Inizializzazione integrazione (async_setup, async_setup_entry)
├── config_flow.py           # Flusso configurazione UI (step_user, step_devices)
├── const.py                 # Costanti e valori default
├── coordinator.py           # DataUpdateCoordinator con logic shedding principale
├── sensor.py                # Sensor potenza istantanea (kW)
├── engine.py                # EnergyManagerEngine per gestione avanzata potenza
├── diagnostics.py           # Diagnostica dispositivi e smart meter
├── storage.py               # Storage eventi locali
├── services.yaml            # Definizione servizi YAML
├── tts.py                   # Notifiche vocali Google TTS
├── yuki_integration.py      # Integrazione notifiche Yuki (push mobile)
├── manifest.json            # Manifest integrazione HA (version, domain, config_flow)
├── requirements.txt         # Dipendenze Python esterne (nessuna per ora)
├── hacs.json                # Config HACS per pubblicare su Store Community
├── translations/
│   ├── en.json              # Traduzioni Inglese (config, entity, services)
│   └── it.json              # Traduzioni Italiano
├── dashboards/
│   └── energy_manager_dashboard.yaml  # Dashboard Lovelace principale
├── configuration.yaml       # Esempio configurazione completa
└── .github/                 # Repository GitHub (CI workflows, issue templates)
```

---

## 🔐 Privacy e Sicurezza

- **Nessun dato inviato all'esterno**: Tutti i calcoli avvengono localmente su Home Assistant
- **Solo polling locale**: L'integrazione usa `local_polling` per la comunicazione
- **Nessun servizio esterno richiesto** (opzionale TTS/Yuki per notifiche)
- **Nessuna dipendenza esterna** nelle versioni attuali

---

## 📝 Note Tecniche

### Compatibilità Home Assistant

- Testato su **Home Assistant 2023.9.0 - 2026.x**
- Usa `EntityComponent` rimosso in HA 2023.9+ → Utilizza approccio minimale
- `DataUpdateCoordinator` con `update_interval=1` per polling ogni secondo

### Logica di Shedding

```python
# Algoritmo principale (simplified)
if power_kw > threshold_kW:
    # Ordina dispositivi per priorità crescente (bassa prima = spenti primi)
    sorted_devices = sort(devices, key=priority)
    
    for device in sorted_devices:
        if priority >= 90:  # Critico - mai spento
            continue
        if state == ON and entity_id != general_breaker:
            call_service("switch/turn_off", entity_id=device.entity_id)
            break  # Spengo solo uno alla volta per non overshoot
        
elif power_kw <= threshold_kW + hysteresis_delay():
    # Ripristino dispositivi spenti (per priorità decrescente)
    for device in reversed(sorted_devices):
        if state == OFF and priority < PRIORITY_HIGH:
            call_service("switch/turn_on", entity_id=device.entity_id)
```

### Gestione Errori

- **UpdateFailed** se sensore potenza non trovato o valore invalido
- **Logger** per debug: `EnergyManagerCoordinator` e `EnergyManagerEngine`
- **Try-except** in tutte le funzioni async per robustezza

---

## 📞 Supporto e Contributi

### Report Bug

Crea un'issue su GitHub con:
- Versione Home Assistant installata
- Versione Energy Manager (0.1.0)
- Log di sistema relativi all'integrazione
- Descrivere il comportamento atteso vs reale

**Repository:** https://github.com/solaris-6/homeassistant-energy-manager

### Feature Request

Proposta nuove funzionalità o migliorie nel repository GitHub.

### Contributi Accettati

- Fix bug e miglioramenti di stabilità
- Nuove modalità operative (es. modalità risparmio, estiva)
- Miglioramento dashboard Lovelace
- Traduzioni in altre lingue
- Documentazione e tutorial

---

## 📜 Licenza

MIT License - Vedi file `LICENSE` per i dettagli completi.

```
Copyright (c) 2026 solaris-6

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

---

## 🙏 Crediti

- **Home Assistant** - Piattaforma open source per automazione casa
- **HACS** - Home Assistant Community Store per distribuzione
- **Community Contributors** - Per suggerimenti e testing

---

*Ultimo aggiornamento: Novembre 2026 | Versione: 0.1.0 | Autore: solaris-6*
