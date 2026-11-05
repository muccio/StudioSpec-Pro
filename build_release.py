#!/usr/bin/env python3
"""
StudioSpec Pro - Release Packaging Script
Generates clean standalone release archives for macOS and Windows.
"""

import os
import sys
import shutil
import zipfile

VERSION = "1.0.0"
DIST_DIR = os.path.join(os.path.dirname(__file__), "dist")

def make_zip(source_dir, output_zip_path):
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            if "__pycache__" in root:
                continue
            for file in files:
                if file.endswith(".pyc") or file == ".DS_Store":
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, source_dir)
                zf.write(full_path, rel_path)

def package_releases():
    os.makedirs(DIST_DIR, exist_ok=True)
    base_dir = os.path.dirname(os.path.abspath(__file__))

    staging_dir = os.path.join(DIST_DIR, "staging")
    if os.path.exists(staging_dir):
        shutil.rmtree(staging_dir)

    # 1. macOS Package
    mac_staging = os.path.join(staging_dir, f"StudioSpecPro-v{VERSION}-macOS")
    os.makedirs(mac_staging, exist_ok=True)
    
    # Copy source folders
    shutil.copytree(os.path.join(base_dir, "studio_inspector"), os.path.join(mac_staging, "studio_inspector"))
    shutil.copytree(os.path.join(base_dir, "web_ui"), os.path.join(mac_staging, "web_ui"))
    shutil.copy2(os.path.join(base_dir, "main.py"), mac_staging)
    shutil.copy2(os.path.join(base_dir, "run.sh"), mac_staging)
    shutil.copy2(os.path.join(base_dir, "README.md"), mac_staging)
    shutil.copy2(os.path.join(base_dir, "pyproject.toml"), mac_staging)
    shutil.copy2(os.path.join(base_dir, "requirements.txt"), mac_staging)

    mac_zip = os.path.join(DIST_DIR, f"StudioSpecPro-v{VERSION}-macOS.zip")
    make_zip(mac_staging, mac_zip)
    print(f"✓ Creato pacchetto macOS: {mac_zip}")

    # 2. Windows Package
    win_staging = os.path.join(staging_dir, f"StudioSpecPro-v{VERSION}-Windows")
    os.makedirs(win_staging, exist_ok=True)

    shutil.copytree(os.path.join(base_dir, "studio_inspector"), os.path.join(win_staging, "studio_inspector"))
    shutil.copytree(os.path.join(base_dir, "web_ui"), os.path.join(win_staging, "web_ui"))
    shutil.copy2(os.path.join(base_dir, "main.py"), win_staging)
    shutil.copy2(os.path.join(base_dir, "run.bat"), win_staging)
    shutil.copy2(os.path.join(base_dir, "README.md"), win_staging)
    shutil.copy2(os.path.join(base_dir, "pyproject.toml"), win_staging)
    shutil.copy2(os.path.join(base_dir, "requirements.txt"), win_staging)

    win_zip = os.path.join(DIST_DIR, f"StudioSpecPro-v{VERSION}-Windows.zip")
    make_zip(win_staging, win_zip)
    print(f"✓ Creato pacchetto Windows: {win_zip}")

    # Clean staging
    shutil.rmtree(staging_dir)
    print("✓ Packaging completato con successo!")

if __name__ == "__main__":
    package_releases()
