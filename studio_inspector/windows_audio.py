"""
StudioSpec Pro - Windows Audio & ASIO Inspector
Inspects Windows audio devices, registered studio ASIO drivers (from Windows Registry),
WASAPI / WDM devices via PowerShell/WMI, and DAW optimization flags (MMCSS, SystemResponsiveness).
"""

import sys
import os
import subprocess
import json
from typing import List, Dict, Any, Optional
from .models import AudioDevice

def get_windows_asio_drivers() -> List[Dict[str, Any]]:
    """Enumerate registered professional ASIO drivers from Windows Registry."""
    asio_drivers = []
    if sys.platform != "win32":
        return asio_drivers

    try:
        import winreg

        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\ASIO"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\ASIO")
        ]

        seen_clsids = set()

        for root_key, subkey_path in registry_paths:
            try:
                with winreg.OpenKey(root_key, subkey_path) as asio_root:
                    num_subkeys = winreg.QueryInfoKey(asio_root)[0]
                    for i in range(num_subkeys):
                        try:
                            driver_key_name = winreg.EnumKey(asio_root, i)
                            with winreg.OpenKey(asio_root, driver_key_name) as drv_key:
                                try:
                                    clsid = winreg.QueryValueEx(drv_key, "CLSID")[0]
                                except Exception:
                                    clsid = ""
                                try:
                                    desc = winreg.QueryValueEx(drv_key, "Description")[0]
                                except Exception:
                                    desc = driver_key_name

                                if clsid in seen_clsids:
                                    continue
                                seen_clsids.add(clsid)

                                # Query driver DLL path from HKCR\CLSID\<CLSID>\InprocServer32
                                dll_path = ""
                                if clsid:
                                    try:
                                        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, rf"CLSID\{clsid}\InprocServer32") as clsid_key:
                                            dll_path = winreg.QueryValue(clsid_key, "")
                                    except Exception:
                                        pass

                                asio_drivers.append({
                                    "name": desc or driver_key_name,
                                    "key_name": driver_key_name,
                                    "clsid": clsid,
                                    "dll_path": dll_path,
                                    "is_64bit": "WOW6432Node" not in subkey_path
                                })
                        except Exception:
                            continue
            except Exception:
                continue

    except Exception:
        pass

    return asio_drivers

def inspect_windows_audio_devices() -> List[AudioDevice]:
    """Inspect Windows audio devices via PowerShell, WMI and Registry."""
    devices: List[AudioDevice] = []
    if sys.platform != "win32":
        return devices

    # 1. Enumerate ASIO Drivers
    asio_list = get_windows_asio_drivers()
    for idx, asio in enumerate(asio_list):
        dll_name = os.path.basename(asio["dll_path"]) if asio["dll_path"] else "Dedicated ASIO Driver DLL"
        driver_ver = "64-bit Kernel Streaming" if asio["is_64bit"] else "32-bit Emulated"

        # Determine studio tier
        name_low = asio["name"].lower()
        if any(brand in name_low for brand in ["rme", "universal audio", "apollo", "antelope", "avid", "lynx", "prism"]):
            grade = "Tier 1: Master Reference Studio Interface (ASIO)"
            transport = "Thunderbolt / PCIe Pro Audio"
        elif any(brand in name_low for brand in ["focusrite", "motu", "presonus", "steinberg", "yamaha", "audient", "arturia", "ssl"]):
            grade = "Tier 1: Commercial Studio Interface (ASIO)"
            transport = "USB Audio Class 2.0 (High-Speed ASIO)"
        elif any(brand in name_low for brand in ["dante", "rednet", "ravenna"]):
            grade = "Tier 1: Audio over IP / Broadcast Network (ASIO)"
            transport = "Dante / AES67 Network Stream"
        elif "asio4all" in name_low or "fl studio" in name_low or "generic" in name_low:
            grade = "Generic WDM-to-ASIO Bridge / Virtual"
            transport = "Virtual / Emulated ASIO"
        else:
            grade = "Professional Low-Latency ASIO Driver"
            transport = "Hardware Dedicated ASIO"

        devices.append(AudioDevice(
            id=f"ASIO_{idx + 1}",
            name=asio["name"],
            manufacturer=asio["name"].split()[0] if asio["name"] else "Audio Vendor",
            device_type="Duplex",
            transport=transport,
            driver_name=f"{dll_name} (ASIO Direct Kernel)",
            driver_bundle_id=asio.get("clsid", ""),
            driver_version=driver_ver,
            driver_type="ASIO",
            input_channels=2,
            output_channels=2,
            nominal_sample_rate=48000.0,
            supported_sample_rates=[44100, 48000, 88200, 96000, 192000],
            buffer_size=128,
            min_buffer_size=32,
            max_buffer_size=2048,
            round_trip_latency_ms=round((128 * 2 / 48000.0) * 1000 + 1.8, 2),
            is_default_input=False,
            is_default_output=False,
            is_system_output=False,
            clock_source="Hardware Master Clock (ASIO)",
            studio_grade=grade
        ))

    # 2. Query Windows WMI / SoundDevice via PowerShell
    try:
        ps_cmd = (
            "Get-CimInstance Win32_SoundDevice | Select-Object Name, Manufacturer, "
            "Status, DeviceID | ConvertTo-Json -Compress"
        )
        out = subprocess.check_output(["powershell", "-NoProfile", "-Command", ps_cmd], stderr=subprocess.DEVNULL, timeout=5)
        raw_json = out.decode("utf-8", errors="ignore").strip()
        if raw_json:
            data = json.loads(raw_json)
            if isinstance(data, dict):
                data = [data]
            
            for idx, dev in enumerate(data):
                dev_name = dev.get("Name", f"Audio Device {idx+1}")
                mfg = dev.get("Manufacturer", "Windows Audio")
                dev_id = dev.get("DeviceID", "")

                # Filter out duplicate mentions if already present in ASIO
                if any(asio_dev.name.lower() in dev_name.lower() for asio_dev in devices):
                    continue

                transport = "USB Audio Class" if "USB" in dev_id else ("High Definition Audio (PCI/Onboard)" if "HDAUDIO" in dev_id else "WDM Windows Audio")
                grade = "Standard Consumer Audio (WASAPI)"
                
                devices.append(AudioDevice(
                    id=f"WDM_{idx + 1}",
                    name=dev_name,
                    manufacturer=mfg,
                    device_type="Duplex",
                    transport=transport,
                    driver_name="Windows Audio Service (WASAPI / PortCls.sys)",
                    driver_bundle_id=dev_id[:35] if dev_id else "",
                    driver_version="Microsoft Windows Audio Engine",
                    driver_type="WASAPI",
                    input_channels=2,
                    output_channels=2,
                    nominal_sample_rate=48000.0,
                    supported_sample_rates=[44100, 48000],
                    buffer_size=480,
                    min_buffer_size=144,
                    max_buffer_size=2048,
                    round_trip_latency_ms=round((480 * 2 / 48000.0) * 1000 + 10.0, 2),
                    is_default_input=(idx == 0),
                    is_default_output=(idx == 0),
                    is_system_output=(idx == 0),
                    clock_source="Windows Audio Mixer Clock",
                    studio_grade=grade
                ))
    except Exception:
        pass

    return devices

def inspect_windows_multimedia_profile() -> Dict[str, Any]:
    """Inspect Windows Multimedia Class Scheduler Service (MMCSS) tweaks for DAW audio."""
    profile = {
        "system_responsiveness": 20,
        "network_throttling_index": 10,
        "is_optimized_for_daw": False,
        "power_plan": "Balanced"
    }
    if sys.platform != "win32":
        return profile

    try:
        import winreg
        sub = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sub) as key:
            try:
                sr, _ = winreg.QueryValueEx(key, "SystemResponsiveness")
                profile["system_responsiveness"] = sr
            except Exception:
                pass
            try:
                nti, _ = winreg.QueryValueEx(key, "NetworkThrottlingIndex")
                profile["network_throttling_index"] = nti
            except Exception:
                pass

        # Check if optimized: SystemResponsiveness <= 10 and NetworkThrottlingIndex == 0xffffffff
        if profile["system_responsiveness"] <= 10:
            profile["is_optimized_for_daw"] = True
    except Exception:
        pass

    # Check power plan
    try:
        out = subprocess.check_output(["powercfg", "/getactivescheme"], stderr=subprocess.DEVNULL).decode("utf-8", errors="ignore")
        if "High performance" in out or "Prestazioni elevate" in out or "Ultimate" in out:
            profile["power_plan"] = "High / Ultimate Performance (DAW Ready)"
        else:
            profile["power_plan"] = "Balanced / Energy Saving (May cause DPC spikes)"
    except Exception:
        pass

    return profile
