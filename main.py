#!/usr/bin/env python3
"""
StudioSpec Pro - Audio Workstation Inspector & Kontakt DFD Benchmark
A cross-platform software for macOS & Windows that evaluates all audio input/output devices,
hardware specifications, driver names, low-latency performance, and disk streaming capabilities
against professional music production workstation standards.

Assigns a studio readiness score out of 100 (voto in centesimi).
"""

import sys
import os
import argparse
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from studio_inspector.core_audio_mac import inspect_macos_audio
from studio_inspector.windows_audio import inspect_windows_audio_devices
from studio_inspector.hardware_specs import get_cpu_specs, get_ram_specs, get_storage_specs, get_os_specs
from studio_inspector.scoring_engine import calculate_studio_score
from studio_inspector.disk_benchmark import get_connected_drives, run_disk_benchmark
from studio_inspector.report_generator import generate_cli_report, generate_markdown_report
from studio_inspector.models import StudioWorkstationReport, DiskBenchmarkResult

def run_diagnostics(include_bench: bool = True, bench_mount: str = "/") -> StudioWorkstationReport:
    """Run full studio workstation scan."""
    import time
    import platform

    system = platform.system()
    if system == "Darwin":
        devices = inspect_macos_audio()
    elif system == "Windows":
        devices = inspect_windows_audio_devices()
    else:
        devices = []

    cpu = get_cpu_specs()
    ram = get_ram_specs()
    storage = get_storage_specs()
    os_info = get_os_specs()
    score = calculate_studio_score(devices, cpu, ram, storage, os_info)

    disk_bench = None
    if include_bench:
        try:
            b_data = run_disk_benchmark(bench_mount, test_size_mb=64)
            disk_bench = DiskBenchmarkResult(**b_data)
        except Exception as e:
            print(f"Nota: Benchmark disco fallito ({e})", file=sys.stderr)

    return StudioWorkstationReport(
        timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
        hostname=platform.node(),
        platform=f"{platform.system()} {platform.machine()}",
        cpu=cpu,
        ram=ram,
        storage=storage,
        os_info=os_info,
        audio_devices=devices,
        score=score,
        disk_benchmark=disk_bench
    )

def main():
    parser = argparse.ArgumentParser(
        description="StudioSpec Pro - Audio Workstation Inspector & Kontakt DFD Benchmark"
    )
    parser.add_argument("--cli", "-c", action="store_true", help="Esegui audit e stampa tabelle nel terminale (modalità CLI)")
    parser.add_argument("--gui", "-g", action="store_true", help="Avvia l'interfaccia grafica Studio Dashboard nel browser")
    parser.add_argument("--json", action="store_true", help="Esporta il report completo in formato JSON")
    parser.add_argument("--markdown", "-m", action="store_true", help="Esporta il report completo in formato Markdown")
    parser.add_argument("--out", "-o", type=str, help="Percorso file di salvataggio per esportazione")
    parser.add_argument("--port", "-p", type=int, default=8844, help="Porta per il server Web locale (default: 8844)")
    parser.add_argument("--no-browser", action="store_true", help="Non aprire automaticamente il browser all'avvio della GUI")
    parser.add_argument("--no-bench", action="store_true", help="Salta il benchmark di lettura/scrittura su disco")
    parser.add_argument("--mount", type=str, default="/", help="Percorso di montaggio disco da testare (default: / o C:\\)")

    args = parser.parse_args()

    # Determine execution mode
    if args.json:
        report = run_diagnostics(include_bench=not args.no_bench, bench_mount=args.mount)
        data_json = json.dumps(report.to_dict(), indent=2)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(data_json)
            print(f"Report JSON salvato in: {args.out}")
        else:
            print(data_json)
        return

    if args.markdown:
        report = run_diagnostics(include_bench=not args.no_bench, bench_mount=args.mount)
        md = generate_markdown_report(report)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(md)
            print(f"Report Markdown salvato in: {args.out}")
        else:
            print(md)
        return

    if args.cli:
        print("\nScansione hardware e periferiche audio in corso...")
        report = run_diagnostics(include_bench=not args.no_bench, bench_mount=args.mount)
        output = generate_cli_report(report)
        print(output)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Report salvato in: {args.out}")
        return

    # Default to GUI Web Dashboard if no CLI flags specified
    try:
        from web_ui.server import start_server
        start_server(port=args.port, open_browser=not args.no_browser)
    except Exception as e:
        print(f"Impossibile avviare la GUI web ({e}). Esecuzione in modalità CLI...\n")
        report = run_diagnostics(include_bench=not args.no_bench, bench_mount=args.mount)
        print(generate_cli_report(report))

if __name__ == "__main__":
    main()
