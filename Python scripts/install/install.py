#!/usr/bin/env python3
"""
📦 Cross-Platform Package Installer Script

This script allows users to:
- Automatically detect the system's package manager.
- Install a given package (by name or .deb/.rpm file).
- Update and upgrade the system using "update" command.

Supported package managers:
- apt (Debian/Ubuntu)
- dnf (Fedora/RHEL/Rocky)
- yum (CentOS/RHEL)
- zypper (openSUSE/SUSE)
- pacman (Arch Linux)

Usage:
    python3 install_tool.py <package-name|update|file.deb|file.rpm>
"""

import sys
import subprocess
import shutil
import os

def run_command(command, check=True):
    """
    Runs a shell command.

    Args:
        command (list): The command to run (as a list of strings).
        check (bool): Whether to raise an error if the command fails.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        print(f"\n$ {' '.join(command)}")
        subprocess.run(command, check=check)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False
    return True

def detect_package_manager():
    """
    Detects the package manager available on the system.

    Returns:
        str: The name of the detected package manager.

    Exits:
        If no supported package manager is found.
    """
    managers = ["apt", "dnf", "yum", "zypper", "pacman"]
    for mgr in managers:
        if shutil.which(mgr):  # Check if the command exists
            return mgr
    print("❌ No supported package manager found.")
    sys.exit(1)

# ----------- Define Command Mappings -------------

# Commands used to update and upgrade system packages
UPDATE_COMMANDS = {
    "apt": [["sudo", "apt-get", "update"], ["sudo", "apt-get", "upgrade", "-y"]],
    "dnf": [["sudo", "dnf", "upgrade", "--refresh", "-y"]],
    "yum": [["sudo", "yum", "update", "-y"]],
    "zypper": [["sudo", "zypper", "refresh"], ["sudo", "zypper", "update", "-y"]],
    "pacman": [["sudo", "pacman", "-Syu", "--noconfirm"]],
}

# Commands used to install named packages (e.g., git, curl)
INSTALL_COMMANDS = {
    "apt": lambda pkg: [["sudo", "apt-get", "install", "-y", pkg]],
    "dnf": lambda pkg: [["sudo", "dnf", "install", "-y", pkg]],
    "yum": lambda pkg: [["sudo", "yum", "install", "-y", pkg]],
    "zypper": lambda pkg: [["sudo", "zypper", "install", "-y", pkg]],
    "pacman": lambda pkg: [["sudo", "pacman", "-S", "--noconfirm", pkg]],
}

# Commands used to install local files (e.g., .deb or .rpm files)
FILE_INSTALLERS = {
    ".deb": lambda pkg: [
        ["sudo", "dpkg", "-i", pkg],
        ["sudo", "apt-get", "install", "-f", "-y"]  # Fix dependencies if needed
    ],
    ".rpm": lambda pkg, mgr: [
        ["sudo", mgr, "install", "-y", pkg]
    ],
}

# ----------- Define Action Functions -------------

def update_system(manager):
    """
    Updates the system using the appropriate package manager commands.

    Args:
        manager (str): The name of the detected package manager.
    """
    for cmd in UPDATE_COMMANDS.get(manager, []):
        run_command(cmd)

def install_package(manager, package):
    """
    Installs a package by name or local file.

    Args:
        manager (str): The detected package manager.
        package (str): The package name or file (.deb/.rpm).
    """
    ext = os.path.splitext(package)[1]

    # Install from .deb or .rpm file
    if ext in FILE_INSTALLERS:
        if ext == ".deb":
            for cmd in FILE_INSTALLERS[ext](package):
                run_command(cmd)
        elif ext == ".rpm":
            for cmd in FILE_INSTALLERS[ext](package, manager):
                run_command(cmd)
        return

    # Install by package name using mapped command
    commands = INSTALL_COMMANDS.get(manager)
    if commands:
        for cmd in commands(package):
            # If apt fails, try to fix broken dependencies
            if not run_command(cmd, check=False) and manager == "apt":
                print("🔧 Fixing broken dependencies...")
                run_command(["sudo", "apt-get", "install", "-f", "-y"])

# ----------- Main Script Entry Point -------------

def main():
    """
    Main function to parse arguments and execute actions.
    """
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <package-name|update|.deb/.rpm>")
        sys.exit(1)

    arg = sys.argv[1]
    manager = detect_package_manager()

    if arg == "update":
        update_system(manager)
    else:
        install_package(manager, arg)

# ------------ Run the Script -------------

if __name__ == "__main__":
    main()
