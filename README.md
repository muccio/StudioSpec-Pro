# 🎛️ StudioSpec Pro
### Audio Workstation Inspector, Driver Diagnostic & Kontakt DFD Benchmark
*Software multipiattaforma per macOS & Windows per l'analisi e il benchmarking di postazioni professionali di produzione musicale e multimediale.*

---

[![Piattaforma](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-blue.svg)](https://github.com/muccio/StudioSpec-Pro)
[![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://www.python.org/)
[![Licenza](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)
[![DAW Benchmark](https://img.shields.io/badge/DAW%20Ready-100%25-orange.svg)]()

## 🌟 Panoramica

**StudioSpec Pro** è un software diagnostico progettato specificamente per le esigenze di compositori, produttori musicali, sound designer e ingegneri del suono. Ispirato alle specifiche tecniche delle workstation impiegate nei grandi studi di registrazione, sale di missaggio Dolby Atmos e scoring stage (Abbey Road, Hans Zimmer Remote Control Productions, Metropolis), StudioSpec Pro effettua una scansione approfondita del computer e dei driver audio, genera tabelle dettagliate e assegna un **voto in centesimi (0 - 100)** con certificazione del livello di produzione (*Tier S+ Elite, Tier A Pro, Tier B Advanced, Tier C Home Studio*).

---

## 🚀 Caratteristiche Principali

### 1. 🎛️ Analisi Approfondita Periferiche Audio & Driver
- **macOS (CoreAudio HAL Nativo via C/ctypes):**
  - Rilevazione a basso livello di tutti i dispositivi di ingresso, uscita e duplex.
  - Identificazione esatta dei **nomi dei driver** e dei bundle installati in `/Library/Audio/Plug-Ins/HAL` (es. *BlackHole64ch.driver, Audiomovers Binaural Renderer, Sonarworks SoundID Reference, ZoomAudioDevice, MSTeamsAudioDevice, Iriun, Apple CoreAudio MacAudio.driver*).
  - Canali di ingresso e uscita, frequenze di campionamento supportate (fino a 192/768 kHz), buffer range (15 - 4096 campioni), safety offset hardware e latenza stimata Round-Trip (RTL) in millisecondi.
  - Identificazione del bus di trasporto: *Thunderbolt 3/4/5 Pro Audio, PCIe, USB Audio Class 2.0, Dante / Ravenna AoIP, Virtual Routing, Aggregate Device*.
- **Windows (ASIO Registry & WASAPI):**
  - Scansione diretta del Registro di Windows (`HKLM\SOFTWARE\ASIO` e `WOW6432Node\ASIO`) per identificare tutti i driver ASIO professionali installati (*Focusrite USB ASIO, RME Fireface, Universal Audio Apollo Thunderbolt, Yamaha Steinberg, MOTU, FL Studio ASIO, ASIO4ALL*).
  - Estrazione dei file DLL del driver da `HKCR\CLSID` e verifica dell'architettura a 64-bit kernel streaming.
  - Verifica delle ottimizzazioni di sistema Windows MMCSS (*SystemResponsiveness, NetworkThrottlingIndex*) e dei piani di alimentazione ad alte prestazioni per evitare picchi di latenza DPC.

### 2. 💻 Hardware Workstation & Specifiche da Studio
- **CPU & Calcolo DSP:** Rilevazione dell'architettura (Apple Silicon M-Series o Intel/AMD Ryzen), distinzione tra **Performance Cores (P-Cores)** dedicati ai thread audio DAW in tempo reale ed **Efficiency Cores (E-Cores)**, clock e vettori di accelerazione SIMD (*ARM NEON, Apple AMX/Accelerate, AVX2, AVX-512* per riverberi convolutivi, filtri e sintetizzatori polifonici).
- **RAM & Banda Passante:** Capacità totale, tipologia di memoria (*Apple Unified Memory fino a 800 GB/s o DDR4/DDR5 multi-channel*) e monitoraggio dello **swap su disco** (per prevenire glitch, clicks e jitter di memoria).
- **Sottosistema OS & Daemon:** Priorità real-time del daemon audio (`coreaudiod` su macOS, `Audiosrv/MMCSS` su Windows) e formati plugin supportati (*AUv2, AUv3, VST3, AAX, CLAP*).

### 3. 💾 Benchmark Disco & Streaming Campionatori (Kontakt DFD)
Include un benchmark dedicato per tutti i dischi collegati (interni ed esterni Thunderbolt/USB):
- **Misurazioni Reali:**
  - Velocità di Scrittura Sequenziale (MB/s) per registrazioni raw a molte tracce.
  - Velocità di Lettura Sequenziale (MB/s) per apertura progetti e caricamento tracce.
  - Velocità di Lettura Random con blocchi a 64 KB (MB/s & IOPS) per simulare l'accesso ai campioni del motore **Direct From Disk (DFD)** di Native Instruments Kontakt, Spitfire Player, Vienna Symphonic Library (VSL) e Sine Player.
- **Calcolo Dinamico delle Patch Kontakt:**
  - **Voci audio simultanee a 48kHz / 24-bit e 96kHz / 24-bit** calcolate con un margine di sicurezza dinamico del 30% per garantire zero buffer underruns.
  - **Patch Orchestrali Pesanti Simultanee:** stima realistica per strumenti multi-microfono con round-robin e release samples (~40 voci attive per patch, es. *Spitfire Symphonic Strings, Berlin Brass, Cinematic Studio*).
  - **Patch Standard Simultanee:** stima per pianoforti a coda, batterie campionate, synth pads e chitarre (~15 voci attive per patch).
  - **Valutazione del Rischio Click & Lag:** da *"Nullo / Assoluta Stabilità"* a *"Rischio Elevato"*.
  - **Buffer DFD Consigliato:** suggerimento pratico sull'impostazione ottimale del Preload Buffer in Kontakt (*Opzioni -> Memory*).

### 4. 🏆 Voto Finale in Centesimi (0 - 100)
Un algoritmo di scoring ponderato basato su 4 categorie:
1. **Audio I/O & Driver Low-Latency:** max 30 punti
2. **CPU & Real-Time DSP Processing:** max 30 punti
3. **RAM & Sample Streaming Bandwidth:** max 25 punti
4. **Storage & Throughput DFD:** max 15 punti

---

## 🖥️ Interfaccia Grafica (Studio Dashboard) & Modalità CLI

StudioSpec Pro offre una **doppia modalità di utilizzo**:

1. **Studio Web Dashboard (Interfaccia Grafica Moderna):**
   - Design Dark Studio Console (grafite e ciano cyber).
   - Indicatore circolare animato del punteggio e badge di classe.
   - Tabella interattiva dei dispositivi audio con ricerca istantanea e filtri (*Tutti, Ingressi, Uscite, Duplex, Studio Pro*).
   - Pannello di controllo benchmark dischi con selezione live del volume.
   - **Calcolatore interattivo di latenza e buffer DAW** con indicatori grafici di usabilità in tempo reale (*IEM monitoring, MIDI recording, Mixing*).
   - Esportazione istantanea in **Markdown (.md)**, **JSON (.json)** o stampa/PDF.

2. **Modalità Terminale (CLI Table Mode):**
   - Tabelle Unicode ad alta leggibilità direttamente nel terminale.
   - Ideale per verifiche veloci, server audio remoti o script automatizzati.

---

## 📦 Download Eseguibili Standalone (v1.0.0)

Non è richiesta alcuna installazione di Python per utilizzare gli eseguibili standalone:

| Piattaforma | File Eseguibile / Pacchetto | Note di Installazione |
|---|---|---|
| **macOS** | [**`StudioSpecPro-macOS.dmg`**](https://github.com/muccio/StudioSpec-Pro/releases/download/v1.0.0/StudioSpecPro-macOS.dmg) (o [`.app.zip`](https://github.com/muccio/StudioSpec-Pro/releases/download/v1.0.0/StudioSpecPro-macOS.app.zip)) | Apri il `.dmg` e trascina **StudioSpec Pro.app** in *Applicazioni*. |
| **Windows** | [**`StudioSpecPro.exe`**](https://github.com/muccio/StudioSpec-Pro/releases/download/v1.0.0/StudioSpecPro.exe) (o [`Standalone.zip`](https://github.com/muccio/StudioSpec-Pro/releases/download/v1.0.0/StudioSpecPro-Windows-x64-Standalone.zip)) | Eseguibile nativo x86-64 a 64-bit pronto con doppio clic. |

---

## 💻 Esecuzione da Sorgente / Script (Python)

### Su macOS:
```bash
# Clona il repository o scarica la release
git clone https://github.com/muccio/StudioSpec-Pro.git
cd StudioSpec-Pro

# Avvio con il launcher one-click (apre la Studio Dashboard nel browser)
./run.sh

# Oppure esecuzione diretta in modalità CLI con tabelle a terminale
./run.sh --cli
```

### Su Windows:
Fai doppio clic sul file **`run.bat`** oppure esegui da prompt PowerShell / CMD:
```cmd
run.bat

REM Per visualizzare le tabelle a riga di comando:
run.bat --cli
```

---

## ⚙️ Opzioni da Riga di Comando (CLI)

```
usage: main.py [-h] [--cli] [--gui] [--json] [--markdown] [--out OUT]
               [--port PORT] [--no-browser] [--no-bench] [--mount MOUNT]

Opzioni:
  --cli, -c       Esegui l'audit e stampa le tabelle nel terminale
  --gui, -g       Avvia la dashboard grafica nel browser (predefinita)
  --json          Esporta il report completo in formato JSON
  --markdown, -m  Esporta il report completo in formato Markdown
  --out, -o FILE  Salva l'output nel file specificato
  --port, -p NUM  Porta per il server Web locale (default: 8844)
  --no-browser    Non aprire automaticamente il browser
  --no-bench      Salta il benchmark di lettura/scrittura su disco
  --mount PATH    Percorso del disco da sottoporre a benchmark (default: / o C:\)
```

### Esempi:
```bash
# Genera un report Markdown e salvalo su file
python3 main.py --markdown --out Studio_Report.md

# Genera un report JSON per l'integrazione con altri strumenti
python3 main.py --json --out specs.json

# Esegui il benchmark su un SSD esterno Thunderbolt montato su /Volumes/AudioSSD
python3 main.py --cli --mount /Volumes/AudioSSD
```

---

## 📊 Criteri di Valutazione delle Workstation da Studio

| Punteggio | Livello / Tier | Destinazione d'Uso Professionale |
|:---:|:---|:---|
| **95 - 100** | 🏆 **Tier S+ Elite Studio** | Scoring Stage per film, Dolby Atmos 7.1.4, oltre 500 tracce, campionatori orchestrali senza purge, mastering a 192 kHz. |
| **85 - 94** | 🥇 **Tier A Pro Studio** | Produzione commerciale, tracking di band dal vivo, mixing multitraccia con pesanti catene analog-modelling. |
| **72 - 84** | 🥈 **Tier B Advanced** | Project studio avanzati, produzione elettronica, arrangiamento e beatmaking complesso. |
| **55 - 71** | 🥉 **Tier C Home Studio** | Songwriting, demo, podcast e produzioni a medio carico (richiede freeze delle tracce). |
| **< 55** | ⚠️ **Tier D Basic** | Configurazione limitata per produzione audio real-time (elevato rischio di dropouts da buffer). |

---

## 📄 Licenza

Rilasciato sotto licenza [MIT](LICENSE). Libero per uso personale e professionale in studio.
Sviluppato da Mario Salvucci.
