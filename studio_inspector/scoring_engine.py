"""
StudioSpec Pro - Scoring & Workstation Benchmarking Engine
Evaluates computer specs and audio devices against professional studio workstation standards
(Hans Zimmer Scoring, Abbey Road, Dolby Atmos mixing stages, commercial mastering).
Produces a comprehensive score out of 100 (voto in centesimi) with detailed category breakdown.
"""

from typing import List, Dict, Any, Tuple
from .models import AudioDevice, CPUSpecs, RAMSpecs, StorageSpecs, OSSpecs, BenchmarkScore

def calculate_studio_score(
    devices: List[AudioDevice],
    cpu: CPUSpecs,
    ram: RAMSpecs,
    storage: StorageSpecs,
    os_info: OSSpecs
) -> BenchmarkScore:
    """Calculate the 100-point studio workstation score."""
    strengths = []
    weaknesses = []
    recommendations = []

    # -------------------------------------------------------------
    # 1. AUDIO I/O & DRIVER ECOSYSTEM (Max 30 pts)
    # -------------------------------------------------------------
    audio_score = 0.0

    # Find highest capability device
    has_thunderbolt_pcie = any("thunderbolt" in d.transport.lower() or "pcie" in d.transport.lower() for d in devices)
    has_usb_interface = any("usb" in d.transport.lower() for d in devices)
    has_pro_routing = any("blackhole" in d.name.lower() or "soundid" in d.name.lower() or "audiomovers" in d.name.lower() or "dante" in d.transport.lower() for d in devices)
    has_asio = any(d.driver_type == "ASIO" for d in devices)
    has_coreaudio = any(d.driver_type == "CoreAudio HAL" for d in devices)

    max_channels_in = max([d.input_channels for d in devices], default=0)
    max_channels_out = max([d.output_channels for d in devices], default=0)
    tot_channels = max_channels_in + max_channels_out

    # Max sample rate supported
    all_sample_rates = []
    for d in devices:
        for sr in d.supported_sample_rates:
            if isinstance(sr, (int, float)):
                all_sample_rates.append(int(sr))
    max_sr = max(all_sample_rates, default=48000)

    # Lowest latency device
    duplex_devices = [d for d in devices if d.device_type in ("Duplex", "Output")]
    min_rtl = min([d.round_trip_latency_ms for d in duplex_devices if d.round_trip_latency_ms > 0], default=15.0)

    # 1.1 Hardware Interface & Driver Tier (Max 12 pts)
    if has_thunderbolt_pcie or (has_asio and has_usb_interface and not any("generic" in d.studio_grade.lower() for d in devices)):
        audio_score += 12.0
        strengths.append("Interfaccia audio Thunderbolt/PCIe o driver ASIO a bassissima latenza hardware.")
    elif has_pro_routing:
        audio_score += 10.0
        strengths.append("Ecosistema di routing professionale attivo (BlackHole 64ch / Audiomovers / SoundID Reference).")
    elif has_usb_interface:
        audio_score += 8.0
        strengths.append("Dispositivo USB Audio Class 2.0 rilevato per produzione musicale.")
    elif has_coreaudio:
        audio_score += 8.0
        strengths.append("Sottosistema Apple CoreAudio HAL a jitter zero con scheduling kernel in tempo reale.")
    else:
        audio_score += 5.0
        weaknesses.append("Nessuna scheda audio dedicata per studio; viene utilizzato l'audio standard di sistema.")
        recommendations.append("Aggiungi una scheda audio professionale USB-C o Thunderbolt (es. Universal Audio Apollo, RME Babyface Pro FS o Focusrite Clarett+) con driver dedicati.")

    # 1.2 Latency & Buffer Range (Max 6 pts)
    if min_rtl <= 5.0:
        audio_score += 6.0
        strengths.append(f"Latenza di monitoraggio in tempo reale eccezionale (RTL stimata: {min_rtl} ms).")
    elif min_rtl <= 10.0:
        audio_score += 4.5
        strengths.append(f"Latenza di monitoraggio buona per registrazione e tracking (RTL stimata: {min_rtl} ms).")
    elif min_rtl <= 16.0:
        audio_score += 3.0
    else:
        audio_score += 1.5
        weaknesses.append(f"Latenza di buffer elevata ({min_rtl} ms), possibile ritardo udibile durante il monitoraggio in cuffia.")
        recommendations.append("Imposta il buffer DAW a 64 o 128 campioni durante la fase di registrazione di voci e strumenti.")

    # 1.3 High-Resolution Sample Rates (Max 5 pts)
    if max_sr >= 192000:
        audio_score += 5.0
        strengths.append(f"Supporto audio ad altissima risoluzione fino a {max_sr // 1000} kHz (Mastering & Sound Design).")
    elif max_sr >= 96000:
        audio_score += 4.0
        strengths.append(f"Supporto audio HD da studio a 96 kHz.")
    elif max_sr >= 48000:
        audio_score += 2.5
    else:
        audio_score += 1.0

    # 1.4 Channel Count / Atmos & Multitrack (Max 4 pts)
    if tot_channels >= 32:
        audio_score += 4.0
        strengths.append(f"Capacità multicanale estesa ({max_channels_in} in / {max_channels_out} out), ideale per Dolby Atmos 7.1.4 e summing analogico.")
    elif tot_channels >= 16:
        audio_score += 3.0
        strengths.append(f"Configurazione I/O estesa ({max_channels_in} in / {max_channels_out} out) per tracking di band e synth hardware.")
    elif tot_channels >= 4:
        audio_score += 2.0
    else:
        audio_score += 1.0
        recommendations.append("Per produzioni Dolby Atmos o tracking multitraccia di batteria, è raccomandata un'interfaccia con almeno 8-16 uscite analogiche/digitali.")

    # 1.5 Driver Stability & Clock (Max 3 pts)
    if any("sonarworks" in d.driver_name.lower() or "soundid" in d.driver_name.lower() for d in devices):
        audio_score += 3.0
        strengths.append("Integrazione driver Sonarworks SoundID Reference attiva per la calibrazione acustica dei monitor da studio.")
    elif has_coreaudio or has_asio:
        audio_score += 3.0
    else:
        audio_score += 1.0

    audio_score = min(30.0, round(audio_score, 1))

    # -------------------------------------------------------------
    # 2. CPU & REAL-TIME DSP PROCESSING (Max 30 pts)
    # -------------------------------------------------------------
    cpu_score = 0.0

    p_cores = cpu.performance_cores
    e_cores = cpu.efficiency_cores
    threads = cpu.logical_threads
    cpu_low = cpu.model.lower()

    # 2.1 Performance Cores (Max 14 pts) - Essential for DAW real-time audio threads
    if p_cores >= 8:
        cpu_score += 14.0
        strengths.append(f"Potenza di calcolo DSP multi-traccia di altissimo livello ({p_cores} Performance Cores dedicati ai thread audio).")
    elif p_cores >= 6:
        cpu_score += 11.0
        strengths.append(f"Ottima disponibilità di core ad alte prestazioni ({p_cores} P-Cores).")
    elif p_cores >= 4:
        cpu_score += 8.0
        strengths.append(f"Capacità di elaborazione adeguata ({p_cores} Core principali).")
    else:
        cpu_score += 4.0
        weaknesses.append(f"Numero limitato di core ad alte prestazioni ({p_cores} P-Cores), rischio di saturazione con plugin pesanti.")
        recommendations.append("Usa il 'Track Freeze' (congelamento tracce) nei progetti complessi per alleggerire la CPU.")

    # 2.2 Architecture & Single-Threaded IPC (Max 8 pts) - Master bus limiters & serial processing
    if any(tag in cpu_low for tag in ["m2 max", "m2 ultra", "m3 max", "m4 max", "m4 pro", "m3 pro", "m1 ultra", "i9-14", "i9-13", "7950x", "9950x"]):
        cpu_score += 8.0
        strengths.append(f"Architettura CPU ammiraglia ({cpu.model}) con IPC elevatissimo per catene di mastering complesse.")
    elif any(tag in cpu_low for tag in ["m1", "m2", "m3", "m4", "i7-13", "i7-14", "7900x", "5950x"]):
        cpu_score += 6.5
        strengths.append("Architettura moderna con eccellente rendimento single-core per elaborazione seriale.")
    elif threads >= 8:
        cpu_score += 5.0
    else:
        cpu_score += 3.0

    # 2.3 Total Logical Threads (Max 4 pts)
    if threads >= 16:
        cpu_score += 4.0
    elif threads >= 10:
        cpu_score += 3.0
    elif threads >= 6:
        cpu_score += 2.0
    else:
        cpu_score += 1.0

    # 2.4 Vector SIMD Acceleration (Max 4 pts)
    if any("neon" in s.lower() or "accelerate" in s.lower() for s in cpu.simd_features) or any("avx2" in s.lower() or "avx-512" in s.lower() for s in cpu.simd_features):
        cpu_score += 4.0
        strengths.append("Accelerazione hardware SIMD / DSP (FFT, riverberi convolutivi, filtri oversampling) attiva.")
    else:
        cpu_score += 2.0

    cpu_score = min(30.0, round(cpu_score, 1))

    # -------------------------------------------------------------
    # 3. RAM & SAMPLE STREAMING BUFFER (Max 25 pts)
    # -------------------------------------------------------------
    ram_score = 0.0
    tot_ram = ram.total_gb

    # 3.1 Total Capacity (Max 18 pts) - Kontakt, VSL, Spitfire, Superior Drummer
    if tot_ram >= 64.0:
        ram_score += 18.0
        strengths.append(f"Dotazione di memoria eccellente ({tot_ram:.0f} GB RAM), ideale per grandi template orchestrali senza purging.")
    elif tot_ram >= 32.0:
        ram_score += 14.5
        strengths.append(f"Ottima memoria RAM ({tot_ram:.0f} GB), perfetta per mix e arrangiamenti professionali complessi.")
    elif tot_ram >= 16.0:
        ram_score += 10.0
        strengths.append(f"RAM sufficiente ({tot_ram:.0f} GB) per produzioni moderne con librerie campionate ottimizzate.")
    elif tot_ram >= 8.0:
        ram_score += 5.0
        weaknesses.append(f"RAM limitata per standard da studio ({tot_ram:.0f} GB). Rischio di freeze con più istanze di campionatori.")
        recommendations.append("Porta la RAM ad almeno 32 GB o 64 GB per caricare librerie come Kontakt, Omnisphere e VSL senza dropouts.")
    else:
        ram_score += 2.0
        weaknesses.append(f"Memoria RAM critica ({tot_ram:.0f} GB), non idonea a produzioni musicali professionali.")

    # 3.2 Memory Architecture & Bandwidth (Max 5 pts)
    if "unified" in ram.memory_type.lower():
        ram_score += 5.0
        strengths.append("Architettura Unified Memory ad altissimo throughput (fino a 400-800 GB/s) condivisa tra CPU e GPU.")
    elif "ddr5" in ram.memory_type.lower():
        ram_score += 4.0
        strengths.append("Memoria DDR5 ad alta frequenza per streaming veloce.")
    else:
        ram_score += 3.0

    # 3.3 Swap & Memory Pressure (Max 2 pts)
    if ram.swap_used_mb == 0.0 or "zero" in ram.swap_pressure.lower() or "low" in ram.swap_pressure.lower():
        ram_score += 2.0
        strengths.append("Nessun paging su disco (Swap = 0 MB): massima reattività e zero jitter di memoria.")
    elif ram.swap_used_mb < 1024:
        ram_score += 1.0
    else:
        weaknesses.append(f"Swap attivo su disco ({ram.swap_used_mb:.0f} MB), potenziale causa di 'clicks and pops' durante l'ascolto.")
        recommendations.append("Chiudi le applicazioni non musicali (browser, suite grafiche) durante le sessioni DAW.")

    ram_score = min(25.0, round(ram_score, 1))

    # -------------------------------------------------------------
    # 4. STORAGE & DFD (DIRECT FROM DISK) THROUGHPUT (Max 15 pts)
    # -------------------------------------------------------------
    storage_score = 0.0

    # 4.1 Drive Protocol & Estimated Speed (Max 10 pts)
    if storage.estimated_speed_mbs >= 4000:
        storage_score += 10.0
        strengths.append(f"Disco di sistema ultra-veloce ({storage.medium_type}, ~{storage.estimated_speed_mbs:.0f} MB/s) per streaming DFD istantaneo.")
    elif storage.estimated_speed_mbs >= 2000:
        storage_score += 8.0
        strengths.append(f"SSD NVMe PCIe veloce (~{storage.estimated_speed_mbs:.0f} MB/s).")
    elif storage.estimated_speed_mbs >= 500:
        storage_score += 5.0
        strengths.append("SSD SATA standard (~500 MB/s).")
    else:
        storage_score += 1.5
        weaknesses.append("Disco meccanico (HDD) rilevato. Grave collo di bottiglia per campionatori e sessioni a molte tracce.")
        recommendations.append("Sposta le librerie campionate e i progetti su un'unità SSD NVMe M.2 o Thunderbolt esterna.")

    # 4.2 Free Space Headroom (Max 5 pts)
    if storage.free_gb >= 100.0:
        storage_score += 5.0
        strengths.append(f"Spazio libero abbondante ({storage.free_gb:.1f} GB disponibili per file audio raw e cache).")
    elif storage.free_gb >= 50.0:
        storage_score += 3.5
    elif storage.free_gb >= 20.0:
        storage_score += 2.0
        weaknesses.append(f"Spazio su disco in esaurimento ({storage.free_gb:.1f} GB liberi).")
        recommendations.append("Mantieni almeno 50-100 GB liberi per la cache di render delle DAW e registrazioni 24-bit/96kHz.")
    else:
        storage_score += 0.5
        weaknesses.append(f"Spazio su disco critico ({storage.free_gb:.1f} GB liberi), rischio interruzione delle registrazioni audio.")

    storage_score = min(15.0, round(storage_score, 1))

    # -------------------------------------------------------------
    # TOTAL SCORE & TIER
    # -------------------------------------------------------------
    total = int(round(audio_score + cpu_score + ram_score + storage_score))
    total = max(10, min(100, total))

    if total >= 95:
        tier = "Tier S+ | Commercial Scoring & Dolby Atmos Mixing Master Rig"
        tier_badge = "S+ ELITE STUDIO"
        tier_desc = "Workstation ai massimi vertici mondiali: idonea a colonne sonore per film con centinaia di tracce, mixing Dolby Atmos 7.1.4, registrazioni orchestrali e mastering professionale senza alcun collo di bottiglia."
    elif total >= 85:
        tier = "Tier A | High-End Professional Studio Rig"
        tier_badge = "TIER A PROFESSIONAL"
        tier_desc = "Workstation di classe professionale: eccellente per produzione commerciale, mixing multitraccia, tracking di band dal vivo e gestione di pesanti catene di plugin con latenze minime."
    elif total >= 72:
        tier = "Tier B | Advanced Project Studio & Producer Rig"
        tier_badge = "TIER B ADVANCED"
        tier_desc = "Configurazione ideale per studi di produzione, produttori elettronici, arrangiatori e songwriter evoluti. Supporta sessioni complesse con ottima stabilità."
    elif total >= 55:
        tier = "Tier C | Home Recording & Songwriting Rig"
        tier_badge = "TIER C HOME STUDIO"
        tier_desc = "Postazione adatta per demo, podcast, songwriting e produzioni a medio carico. Richiede gestione oculata dei buffer e freeze delle tracce."
    else:
        tier = "Tier D | Basic / Unoptimized for Real-time Pro Audio"
        tier_badge = "TIER D BASIC"
        tier_desc = "Configurazione limitata per produzione audio in tempo reale. Rischio di dropouts, latenza elevata e saturazione delle risorse."

    # DAW Use Case Readiness
    daw_profiles = [
        {
            "use_case": "Orchestral Scoring & Huge Sample Templates (Kontakt, VSL, Spitfire)",
            "rating": "Eccellente (Tier S+)" if tot_ram >= 64 and p_cores >= 8 else ("Ottimo" if tot_ram >= 32 else "Limitato da RAM"),
            "score_pct": min(100, int((tot_ram / 64.0) * 50 + (p_cores / 8.0) * 50)),
            "comment": f"{tot_ram:.0f}GB RAM + {p_cores} P-Cores permettono streaming orchestrale fluido senza purging."
        },
        {
            "use_case": "Dolby Atmos 7.1.4 & Immersive Audio Mixing",
            "rating": "Eccellente" if tot_channels >= 16 and p_cores >= 8 else ("Ottimo con Routing Virtuale" if has_pro_routing else "Richiede I/O multicanale"),
            "score_pct": min(100, int((tot_channels / 16.0) * 40 + (p_cores / 8.0) * 60)),
            "comment": "Bed 7.1.2 + Object beds gestibili con renderer Dolby Atmos e routing a bassissima latenza."
        },
        {
            "use_case": "Live Band Multi-Track Recording (24-bit / 96kHz, 16+ canali)",
            "rating": "Idoneo con Zero Jitter" if (has_coreaudio or has_asio) and max_sr >= 96000 else "Standard",
            "score_pct": min(100, int((max_sr / 96000.0) * 50 + (storage.estimated_speed_mbs / 4000.0) * 50)),
            "comment": f"Buffer sicuro, disco NVMe da {storage.estimated_speed_mbs:.0f} MB/s e clock stabile."
        },
        {
            "use_case": "Electronic Music, Heavy Synth & Beatmaking (Ableton, FL, Logic)",
            "rating": "Massima Reattività",
            "score_pct": min(100, int((p_cores / 8.0) * 60 + (ram_score / 25.0) * 40)),
            "comment": "Polifonia estesa per Serum, Diva, Omnisphere e catene oversampling in tempo reale."
        },
        {
            "use_case": "Mastering & High-Resolution Stereo Delivery (192kHz)",
            "rating": "Certificato Studio Master" if max_sr >= 192000 else "Standard 96kHz",
            "score_pct": min(100, int((max_sr / 192000.0) * 50 + (cpu_score / 30.0) * 50)),
            "comment": f"Supporto formati fino a {max_sr // 1000} kHz e calcoli in virgola mobile a 64-bit."
        }
    ]

    return BenchmarkScore(
        total_score=total,
        tier=tier,
        tier_badge=tier_badge,
        tier_description=tier_desc,
        audio_io_score=audio_score,
        cpu_dsp_score=cpu_score,
        ram_sample_score=ram_score,
        storage_dfd_score=storage_score,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
        daw_readiness=daw_profiles
    )
