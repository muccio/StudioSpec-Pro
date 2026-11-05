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
    # Filter out macOS Finder Process Serial Number arguments (e.g. -psn_0_12345)
    clean_argv = [arg for arg in sys.argv[1:] if not arg.startswith("-psn")]

    parser = argparse.ArgumentParser(
        description="StudioSpec Pro - Audio Workstation Inspector & Kontakt DFD Benchmark"
    )
    parser.add_argument("--cli", "-c", action="store_true", help="Esegui audit e stampa tabelle nel terminale (modalità CLI)")
    parser.add_argument("--gui", "-g", action="store_true", help="Avvia l'applicazione desktop nativa (predefinita)")
    parser.add_argument("--browser", action="store_true", help="Forza l'apertura della dashboard nel browser web anziché nella finestra nativa")
    parser.add_argument("--json", action="store_true", help="Esporta il report completo in formato JSON")
    parser.add_argument("--markdown", "-m", action="store_true", help="Esporta il report completo in formato Markdown")
    parser.add_argument("--out", "-o", type=str, help="Percorso file di salvataggio per esportazione")
    parser.add_argument("--port", "-p", type=int, default=8844, help="Porta per il server Web locale (default: 8844)")
    parser.add_argument("--no-browser", action="store_true", help="Non aprire automaticamente il browser all'avvio della GUI")
    parser.add_argument("--no-bench", action="store_true", help="Salta il benchmark di lettura/scrittura su disco")
    parser.add_argument("--mount", type=str, default="/", help="Percorso di montaggio disco da testare (default: / o C:\\)")

    args = parser.parse_args(clean_argv)

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

    # Default: Native Standalone Desktop Window (PyWebView)
    try:
        if args.browser:
            from web_ui.server import start_server
            start_server(port=args.port, open_browser=True)
            return

        import threading
        import socket
        from http.server import HTTPServer
        from web_ui.server import StudioHandler

        # Find available port
        port = args.port
        for p in [port, 8845, 8846, 8847, 8848, 8849, 8850]:
            try:
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_sock.bind(("127.0.0.1", p))
                test_sock.close()
                port = p
                break
            except OSError:
                continue

        # Start background server
        httpd = HTTPServer(("127.0.0.1", port), StudioHandler)
        srv_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        srv_thread.start()

        # Try launching Native Standalone Window via pywebview
        try:
            import webview
            window = webview.create_window(
                title="StudioSpec Pro - Audio Workstation Inspector & Kontakt DFD Benchmark",
                url=f"http://127.0.0.1:{port}",
                width=1340,
                height=880,
                min_size=(1020, 680),
                background_color="#0a0e17",
                text_select=True
            )
            webview.start()
        except ImportError:
            # Fallback to web browser if pywebview is not installed in the python environment
            print("\nNota: Per la finestra nativa desktop, installa pywebview (`pip install pywebview`).")
            print(f"Apertura dashboard nel browser su: http://localhost:{port}\n")
            import webbrowser
            webbrowser.open(f"http://localhost:{port}")
            try:
                srv_thread.join()
            except KeyboardInterrupt:
                pass

    except Exception as e:
        print(f"Impossibile avviare la GUI ({e}). Esecuzione in modalità CLI...\n")
        report = run_diagnostics(include_bench=not args.no_bench, bench_mount=args.mount)
        print(generate_cli_report(report))

if __name__ == "__main__":
    main()
