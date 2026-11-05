"""
StudioSpec Pro - Report Generator
Generates clean terminal tables, Markdown documentation, and standalone HTML/JSON reports.
"""

import json
from typing import List, Dict, Any
from .models import StudioWorkstationReport, AudioDevice

def format_cli_table(headers: List[str], rows: List[List[str]], title: str = "") -> str:
    """Format a clean, professional ASCII/Unicode border table for the terminal."""
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(val)))

    # Formatting borders
    top_border = "┌─" + "─┬─".join("─" * w for w in col_widths) + "─┐"
    header_sep = "├─" + "─┼─".join("─" * w for w in col_widths) + "─┤"
    bot_border = "└─" + "─┴─".join("─" * w for w in col_widths) + "─┘"

    header_line = "│ " + " │ ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths)) + " │"
    
    table_lines = []
    if title:
        table_lines.append(f"\n\033[1;36m▶ {title.upper()}\033[0m")
    table_lines.append(top_border)
    table_lines.append(header_line)
    table_lines.append(header_sep)

    for row in rows:
        line = "│ " + " │ ".join(f"{str(v):<{w}}" for v, w in zip(row, col_widths)) + " │"
        table_lines.append(line)

    table_lines.append(bot_border)
    return "\n".join(table_lines)

def generate_cli_report(report: StudioWorkstationReport) -> str:
    """Generate the complete multi-table CLI studio audit."""
    lines = []
    score = report.score

    # Studio Title Header
    lines.append("\n" + "=" * 90)
    lines.append("  🎛️  STUDIOSPEC PRO - AUDIO WORKSTATION & HARDWARE INSPECTOR")
    lines.append(f"  Host: {report.hostname} | Platform: {report.platform} | Audit Date: {report.timestamp}")
    lines.append("=" * 90)

    # Big Score Box
    score_banner = f"""
  ╔═══════════════════════════════════════════════════════════════════════════════════╗
  ║  VOTO STUDIOPRO:  \033[1;32m{score.total_score:3d} / 100\033[0m                                                      ║
  ║  CLASSIFICAZIONE: \033[1;33m{score.tier_badge:<20}\033[0m                                          ║
  ║  {score.tier:<81}║
  ╚═══════════════════════════════════════════════════════════════════════════════════╝
    """
    lines.append(score_banner)

    # 1. Hardware Specs Table
    hw_headers = ["Parametro", "Specifiche Hardware Rilevate", "Impatto Studio DAW"]
    hw_rows = [
        ["Modello CPU", report.cpu.model, "Calcolo DSP, Polyfonia e catene Master"],
        ["Architettura & Core", f"{report.cpu.physical_cores} Cores ({report.cpu.performance_cores} P-Cores, {report.cpu.efficiency_cores} E-Cores)", "Core ad alte prestazioni per thread audio"],
        ["Istruzioni Vettoriali / SIMD", ", ".join(report.cpu.simd_features[:2]), "Accelerazione FFT, Riverberi convolutivi"],
        ["Memoria RAM Totale", f"{report.ram.total_gb:.1f} GB ({report.ram.memory_type})", "Capacità campionatori (Kontakt, Spitfire)"],
        ["Stato Swap Memoria", f"{report.ram.swap_used_mb:.1f} MB ({report.ram.swap_pressure})", "Zero dropouts e latenza jitter"],
        ["Disco di Sistema", f"{report.storage.primary_drive_name} ({report.storage.medium_type})", f"Streaming DFD: {report.storage.dfd_streaming_readiness[:25]}"],
        ["Spazio Libero", f"{report.storage.free_gb:.1f} GB ({report.storage.free_percentage:.1f}%)", "Spazio cache registrazione 24-bit/96k"],
        ["Sistema Operativo", report.os_info.os_name, report.os_info.audio_subsystem[:40]],
        ["Formati Plugin Supportati", ", ".join(report.os_info.plugin_formats_supported[:4]), "Standard VST3/AU/AAX nativi"]
    ]
    lines.append(format_cli_table(hw_headers, hw_rows, "Caratteristiche Hardware Workstation"))

    # 1.1 Disk Benchmark & Kontakt DFD Streaming Table (if available)
    if report.disk_benchmark:
        db = report.disk_benchmark
        db_headers = ["Parametro Benchmark Disco", "Valore Misurato", "Impatto Produzione / Kontakt DFD"]
        db_rows = [
            ["Unità Testata", db.mount_point, "Percorso volume storage"],
            ["Velocità Scrittura Sequenziale", f"{db.write_speed_mbs:.1f} MB/s", "Registrazione multitraccia raw contemporanea"],
            ["Velocità Lettura Sequenziale", f"{db.seq_read_speed_mbs:.1f} MB/s", "Caricamento iniziale campioni e progetti"],
            ["Velocità Lettura Random 64KB (DFD)", f"{db.rnd_read_speed_mbs:.1f} MB/s ({db.rnd_iops} IOPS)", "Prestazioni effettive durante riproduzione campionatori"],
            ["Throughput DFD Sicuro (Headroom 70%)", f"{db.effective_dfd_bandwidth_mbs:.1f} MB/s", "Banda disponibile con zero glitch"],
            ["VOCI AUDIO SIMULTANEE (48kHz/24-bit)", f"{db.max_voices_48k:,} voci", "Flussi audio contemporanei dal disco senza lag"],
            ["VOCI AUDIO SIMULTANEE (96kHz/24-bit)", f"{db.max_voices_96k:,} voci", "Streaming in alta definizione"],
            ["PATCH KONTAKT ORCHESTRALI PESANTI", f"~{db.patches_heavy_48k} patch simultanee", "Spitfire/Berlin Strings (multi-microfono ~40 voci/patch)"],
            ["PATCH KONTAKT STANDARD / PIANOFORTI", f"~{db.patches_standard_48k} patch simultanee", "Pianoforti, Synth, Kit di batteria (~15 voci/patch)"],
            ["RISCHIO CLICK & LAG IN RIPRODUZIONE", db.click_risk, "Stabilità durante accordi veloci e sustain"],
            ["BUFFER KONTAKT DFD CONSIGLIATO", db.recommended_kontakt_dfd_buffer, "Impostazione ottimale in Opzioni Kontakt -> Memory"],
            ["VALUTAZIONE DISCO", db.assessment[:45], "Certificazione storage studio"]
        ]
        lines.append(format_cli_table(db_headers, db_rows, "Benchmark Disco & Capacità Streaming Campionatori (Kontakt DFD)"))

    # 2. Audio Devices Table
    dev_headers = ["Dispositivo Audio", "Produttore", "Driver Periferica Rilevato", "Tipo / I/O", "Sample Rate Max", "RTL (Est.)", "Ruolo / Grado"]
    dev_rows = []
    for d in report.audio_devices:
        sr_max = max([int(s) for s in d.supported_sample_rates if isinstance(s, (int, float))], default=48000)
        ch_str = f"{d.input_channels} In / {d.output_channels} Out"
        rtl_str = f"{d.round_trip_latency_ms:.1f} ms"
        role_marker = "★ PREDEF " if (d.is_default_output or d.is_default_input) else ""
        dev_rows.append([
            f"{role_marker}{d.name[:24]}",
            d.manufacturer[:14],
            f"{d.driver_name[:28]}",
            f"{d.transport[:14]} ({ch_str})",
            f"{sr_max // 1000} kHz",
            rtl_str,
            d.studio_grade[:25]
        ])
    lines.append(format_cli_table(dev_headers, dev_rows, f"Elenco Periferiche Audio & Driver ({len(report.audio_devices)} Rilevate)"))

    # 3. Score Breakdown Table
    score_headers = ["Area di Valutazione Studio", "Punteggio", "Peso Max", "Valutazione Professionale"]
    score_rows = [
        ["Audio I/O & Driver Low-Latency", f"{score.audio_io_score:.1f}", "30 pt", "Driver dedicato, stabilità clock e canali"],
        ["CPU & Real-Time DSP Processing", f"{score.cpu_dsp_score:.1f}", "30 pt", "P-Cores, IPC single-core e accelerazione SIMD"],
        ["RAM & Sample Streaming Bandwidth", f"{score.ram_sample_score:.1f}", "25 pt", "Capacità e bandwidth per template orchestrali"],
        ["Storage & Throughput DFD", f"{score.storage_dfd_score:.1f}", "15 pt", "Velocità di lettura NVMe e spazio libero"],
        ["TOTALE FINALE IN CENTESIMI", f"{score.total_score}", "100 pt", score.tier_badge]
    ]
    lines.append(format_cli_table(score_headers, score_rows, "Dettaglio Punteggio Studio (Voto in Centesimi)"))

    # 4. DAW Readiness Table
    daw_headers = ["Ambito di Produzione Musicale", "Idoneità Workstation", "Indice", "Analisi Tecnica"]
    daw_rows = []
    for daw in score.daw_readiness:
        daw_rows.append([
            daw["use_case"][:38],
            daw["rating"],
            f"{daw['score_pct']}%",
            daw["comment"][:45]
        ])
    lines.append(format_cli_table(daw_headers, daw_rows, "Idoneità Applicativa (DAW Workflows)"))

    # 5. Strengths & Recommendations
    if score.strengths:
        lines.append("\n\033[1;32m✓ PUNTI DI FORZA DELLA WORKSTATION:\033[0m")
        for s in score.strengths:
            lines.append(f"  • {s}")

    if score.weaknesses:
        lines.append("\n\033[1;31m⚠ LIMITAZIONI O CRITICITÀ RILEVATE:\033[0m")
        for w in score.weaknesses:
            lines.append(f"  • {w}")

    if score.recommendations:
        lines.append("\n\033[1;33m💡 RACCOMANDAZIONI DI OTTIMIZZAZIONE PER LA PRODUZIONE:\033[0m")
        for r in score.recommendations:
            lines.append(f"  ➜ {r}")

    lines.append("\n" + "=" * 90 + "\n")
    return "\n".join(lines)

def generate_markdown_report(report: StudioWorkstationReport) -> str:
    """Generate Markdown report suitable for documentation or GitHub."""
    s = report.score
    md = []
    md.append(f"# StudioSpec Pro - Report Diagnostico Workstation Audio\n")
    md.append(f"- **Data Scansione:** {report.timestamp}")
    md.append(f"- **Host:** `{report.hostname}` | **Piattaforma:** `{report.platform}`\n")
    md.append(f"## 🏆 Voto Finale: {s.total_score} / 100 ({s.tier_badge})\n")
    md.append(f"> **{s.tier}**\n>\n> {s.tier_description}\n")

    md.append("### 📊 Tabella Punteggio in Centesimi\n")
    md.append("| Categoria | Punteggio | Max | Valutazione |")
    md.append("|---|---|---|---|")
    md.append(f"| **Audio I/O & Driver** | {s.audio_io_score:.1f} | 30 | Interfaccia, clock e latenza |")
    md.append(f"| **CPU & Elaborazione DSP** | {s.cpu_dsp_score:.1f} | 30 | Performance Cores e vettori SIMD |")
    md.append(f"| **RAM & Sample Streaming** | {s.ram_sample_score:.1f} | 25 | Capacità template e banda passante |")
    md.append(f"| **Storage & Throughput DFD** | {s.storage_dfd_score:.1f} | 15 | Velocità SSD e spazio libero |")
    md.append(f"| **VOTO COMPLESSIVO** | **{s.total_score}** | **100** | **{s.tier_badge}** |\n")

    md.append("### 🎛️ Tabella Dispositivi Audio & Driver\n")
    md.append("| Dispositivo | Produttore | Driver Periferica | Connessione | I/O | Sample Rate | Latency RTL | Grado Studio |")
    md.append("|---|---|---|---|---|---|---|---|")
    for d in report.audio_devices:
        sr_max = max([int(x) for x in d.supported_sample_rates if isinstance(x, (int, float))], default=48000)
        def_tag = " (Default)" if d.is_default_output else ""
        md.append(f"| {d.name}{def_tag} | {d.manufacturer} | `{d.driver_name}` | {d.transport} | {d.input_channels}in/{d.output_channels}out | {sr_max} Hz | {d.round_trip_latency_ms} ms | {d.studio_grade} |")

    md.append("\n### 💻 Specifiche Hardware della Workstation\n")
    md.append("| Componente | Dettagli Tecnici | Impatto DAW |")
    md.append("|---|---|---|")
    md.append(f"| **Processore (CPU)** | {report.cpu.model} | {report.cpu.performance_cores} P-Cores, {report.cpu.efficiency_cores} E-Cores ({report.cpu.logical_threads} threads) |")
    md.append(f"| **Accelerazione SIMD** | {', '.join(report.cpu.simd_features)} | Ottimizzazione riverberi convolutivi e filtri |")
    md.append(f"| **Memoria RAM** | {report.ram.total_gb:.1f} GB ({report.ram.memory_type}) | Paging disco: {report.ram.swap_used_mb} MB ({report.ram.swap_pressure}) |")
    md.append(f"| **Disco & Archiviazione** | {report.storage.primary_drive_name} ({report.storage.medium_type}) | Streaming DFD: {report.storage.dfd_streaming_readiness} (~{report.storage.estimated_speed_mbs} MB/s) |")
    md.append(f"| **Spazio Libero** | {report.storage.free_gb:.1f} GB liberi su {report.storage.total_gb:.1f} GB | Headroom progetti e cache di freeze |")
    md.append(f"| **Sistema & Daemon Audio** | {report.os_info.os_name} | Subsystem: {report.os_info.audio_subsystem} |")
    md.append(f"| **Plugin Supportati** | {', '.join(report.os_info.plugin_formats_supported)} | Standard compatibili |")

    if report.disk_benchmark:
        db = report.disk_benchmark
        md.append("\n### 💾 Benchmark Disco & Capacità Streaming Campioni (Kontakt DFD)\n")
        md.append("| Metrica Benchmark | Risultato Misurato | Significato Operativo |")
        md.append("|---|---|---|")
        md.append(f"| **Velocità Scrittura** | **{db.write_speed_mbs:.1f} MB/s** | Registrazione multitraccia raw |")
        md.append(f"| **Velocità Lettura Sequenziale** | **{db.seq_read_speed_mbs:.1f} MB/s** | Caricamento iniziale progetti e file audio |")
        md.append(f"| **Velocità Lettura Random 64KB (DFD)** | **{db.rnd_read_speed_mbs:.1f} MB/s** ({db.rnd_iops} IOPS) | Throughput campioni durante esecuzione |")
        md.append(f"| **Voci Audio Simultanee (48kHz/24-bit)** | **{db.max_voices_48k:,} voci** | Flussi audio continui senza dropouts |")
        md.append(f"| **Voci Audio Simultanee (96kHz/24-bit)** | **{db.max_voices_96k:,} voci** | Streaming HD a 96kHz |")
        md.append(f"| **Patch Orchestrali Pesanti (Spitfire/Berlin)** | **~{db.patches_heavy_48k} patch** | Template multi-microfono (~40 voci/patch) |")
        md.append(f"| **Patch Standard (Piani, Synth, Batterie)** | **~{db.patches_standard_48k} patch** | Strumenti standard (~15 voci/patch) |")
        md.append(f"| **Rischio Click, Lag & Crackle** | **{db.click_risk}** | Stabilità tempo reale |")
        md.append(f"| **Buffer DFD Consigliato in Kontakt** | **{db.recommended_kontakt_dfd_buffer}** | Impostazione memoria Kontakt DFD |")
        md.append(f"| **Giudizio Prestazionale Storage** | **{db.assessment}** | Certificazione per scoring stage |")

    md.append("\n### 🎹 Idoneità Flussi di Lavoro DAW\n")
    md.append("| Flusso di Lavoro | Idoneità | Punteggio | Dettaglio Tecnico |")
    md.append("|---|---|---|---|")
    for daw in s.daw_readiness:
        md.append(f"| {daw['use_case']} | {daw['rating']} | {daw['score_pct']}% | {daw['comment']} |")

    if s.strengths:
        md.append("\n### ✅ Punti di Forza\n")
        for st in s.strengths:
            md.append(f"- {st}")

    if s.recommendations:
        md.append("\n### 💡 Raccomandazioni Tecniche per lo Studio\n")
        for rec in s.recommendations:
            md.append(f"- {rec}")

    return "\n".join(md)
