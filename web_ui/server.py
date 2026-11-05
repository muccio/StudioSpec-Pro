"""
StudioSpec Pro - Embedded Local Web Server & API
Provides a zero-dependency local HTTP server and REST API for the Studio Dashboard.
"""

import os
import sys
import json
import socket
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Optional, Any, List, Dict

from studio_inspector.core_audio_mac import inspect_macos_audio
from studio_inspector.windows_audio import inspect_windows_audio_devices
from studio_inspector.hardware_specs import get_cpu_specs, get_ram_specs, get_storage_specs, get_os_specs
from studio_inspector.scoring_engine import calculate_studio_score
from studio_inspector.disk_benchmark import get_connected_drives, run_disk_benchmark
from studio_inspector.report_generator import generate_markdown_report
from studio_inspector.models import StudioWorkstationReport, DiskBenchmarkResult

def get_web_ui_dir() -> str:
    """Resolve correct web_ui directory whether running from source or frozen PyInstaller .app/.exe."""
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            cand1 = os.path.join(meipass, "web_ui")
            if os.path.isdir(cand1):
                return cand1
            if os.path.isdir(os.path.join(meipass, "templates")):
                return meipass

        exe_dir = os.path.dirname(sys.executable)
        cand2 = os.path.normpath(os.path.join(exe_dir, "..", "Resources", "web_ui"))
        if os.path.isdir(cand2):
            return cand2
        cand3 = os.path.join(exe_dir, "web_ui")
        if os.path.isdir(cand3):
            return cand3

    return os.path.dirname(os.path.abspath(__file__))

def build_full_report(run_initial_bench: bool = False, bench_mount: str = "/") -> StudioWorkstationReport:
    """Scan workstation and build comprehensive report."""
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
    if run_initial_bench:
        try:
            b_data = run_disk_benchmark(bench_mount, test_size_mb=64)
            disk_bench = DiskBenchmarkResult(**b_data)
        except Exception:
            pass

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

class StudioHandler(BaseHTTPRequestHandler):
    cached_report: Optional[StudioWorkstationReport] = None
    
    @property
    def static_dir(self) -> str:
        return os.path.join(get_web_ui_dir(), "static")

    @property
    def templates_dir(self) -> str:
        return os.path.join(get_web_ui_dir(), "templates")

    def log_message(self, format, *args):
        # Suppress standard noisy access logging
        return

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            self.serve_template("index.html", "text/html; charset=utf-8")
        elif path == "/api/report":
            if not StudioHandler.cached_report:
                StudioHandler.cached_report = build_full_report(run_initial_bench=True)
            self.send_json(StudioHandler.cached_report.to_dict())
        elif path == "/api/refresh":
            StudioHandler.cached_report = build_full_report(run_initial_bench=False)
            self.send_json(StudioHandler.cached_report.to_dict())
        elif path == "/api/drives":
            drives = get_connected_drives()
            self.send_json({"drives": drives})
        elif path == "/export/markdown":
            if not StudioHandler.cached_report:
                StudioHandler.cached_report = build_full_report(run_initial_bench=True)
            md = generate_markdown_report(StudioHandler.cached_report)
            self.send_response(200)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="StudioSpec_Report.md"')
            self.end_headers()
            self.wfile.write(md.encode("utf-8"))
        elif path == "/export/json":
            if not StudioHandler.cached_report:
                StudioHandler.cached_report = build_full_report(run_initial_bench=True)
            js_data = json.dumps(StudioHandler.cached_report.to_dict(), indent=2)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="StudioSpec_Report.json"')
            self.end_headers()
            self.wfile.write(js_data.encode("utf-8"))
        elif path.startswith("/static/"):
            filename = path.replace("/static/", "")
            file_path = os.path.join(self.static_dir, filename)
            if os.path.exists(file_path):
                mime = "text/css" if filename.endswith(".css") else ("application/javascript" if filename.endswith(".js") else "text/plain")
                self.serve_file(file_path, mime)
            else:
                self.send_error(404, "File not found")
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/benchmark":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len) if content_len > 0 else b"{}"
            try:
                params = json.loads(post_body.decode("utf-8"))
            except Exception:
                params = {}

            mount = params.get("mount_point", "/")
            size_mb = int(params.get("size_mb", 64))

            res = run_disk_benchmark(mount, test_size_mb=size_mb)
            
            # Update cached report with new benchmark
            if StudioHandler.cached_report:
                StudioHandler.cached_report.disk_benchmark = DiskBenchmarkResult(**res)

            self.send_json(res)
        else:
            self.send_error(404, "Not Found")

    def send_json(self, data: Any):
        json_bytes = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(json_bytes)))
        self.end_headers()
        self.wfile.write(json_bytes)

    def serve_file(self, file_path: str, content_type: str):
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception:
            self.send_error(500, "Error reading file")

    def serve_template(self, filename: str, content_type: str):
        tpl_path = os.path.join(self.templates_dir, filename)
        if os.path.exists(tpl_path):
            self.serve_file(tpl_path, content_type)
        else:
            self.send_error(404, f"Template {filename} not found")

def start_server(port: int = 8844, open_browser: bool = True):
    """Start local web server and open dashboard."""
    server_address = ("127.0.0.1", port)
    try:
        httpd = HTTPServer(server_address, StudioHandler)
    except OSError:
        # Try next port if 8844 is busy
        port = 8845
        server_address = ("127.0.0.1", port)
        httpd = HTTPServer(server_address, StudioHandler)

    url = f"http://localhost:{port}"
    print(f"\n\033[1;32m✓ StudioSpec Pro Dashboard avviato su: {url}\033[0m")
    print(f"  Premi Ctrl+C nel terminale per arrestare il server.\n")

    if open_browser:
        webbrowser.open(url)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nArresto server in corso...")
        httpd.server_close()
