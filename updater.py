"""
Auto-updater for Buckeling Automation

Checks GitHub releases for updates and provides functionality to download
and install new versions automatically.
"""

import urllib.request
import json
import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox
from version import __version__


class AutoUpdater:
    """Handles checking for updates and automatic application updates"""
    
    GITHUB_REPO = "Bluefly-Hub/Buckeling_Automation"
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    # Optional: Add your GitHub Personal Access Token here for private repos
    # Create token at: https://github.com/settings/tokens (needs 'repo' scope)
    GITHUB_TOKEN = None  # Set to "ghp_yourtoken..." for private repos
    
    def __init__(self):
        self.current_version = __version__
    
    def check_for_updates(self):
        """
        Check GitHub for the latest release
        Returns: (bool, str, str) - (update_available, latest_version, download_url)
        """
        try:
            # Make request to GitHub API
            headers = {'User-Agent': 'BuckelingAutomation-Updater'}
            if self.GITHUB_TOKEN:
                headers['Authorization'] = f'token {self.GITHUB_TOKEN}'
            
            req = urllib.request.Request(self.GITHUB_API_URL, headers=headers)
            
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                
            latest_version = data.get('tag_name', '').lstrip('v')
            
            # Find the .exe asset in the release
            download_url = None
            for asset in data.get('assets', []):
                if asset['name'].endswith('.exe'):
                    download_url = asset['browser_download_url']
                    break
            
            if not download_url:
                return False, latest_version, None
                
            # Compare versions
            update_available = self._is_newer_version(latest_version, self.current_version)
            
            return update_available, latest_version, download_url
            
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return False, None, None
    
    def _is_newer_version(self, latest, current):
        """Compare version strings (e.g., '1.2.3' vs '1.2.2')"""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Pad with zeros if needed
            while len(latest_parts) < len(current_parts):
                latest_parts.append(0)
            while len(current_parts) < len(latest_parts):
                current_parts.append(0)
            
            return latest_parts > current_parts
        except:
            return False
    
    def download_and_install_update(self, download_url, latest_version):
        """
        Download the new version and replace the current executable
        Returns: bool - Success status
        """
        try:
            # Get current executable path
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
            else:
                # For testing in development
                current_exe = os.path.abspath(sys.argv[0])
            
            exe_dir = os.path.dirname(current_exe)
            temp_exe = os.path.join(exe_dir, 'BuckelingAutomation_new.exe')
            backup_exe = os.path.join(exe_dir, 'BuckelingAutomation_backup.exe')
            
            # Download new version
            print(f"Downloading update from {download_url}...")
            urllib.request.urlretrieve(download_url, temp_exe)
            
            # Create batch file to replace the executable
            batch_file = os.path.join(exe_dir, 'update.bat')
            batch_content = f"""@echo off
timeout /t 2 /nobreak > nul
move /y "{current_exe}" "{backup_exe}"
move /y "{temp_exe}" "{current_exe}"
start "" "{current_exe}"
del "%~f0"
"""
            
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            # Run the batch file and exit
            subprocess.Popen(['cmd', '/c', batch_file], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            return True
            
        except Exception as e:
            print(f"Error installing update: {e}")
            # Clean up temp files
            if os.path.exists(temp_exe):
                try:
                    os.remove(temp_exe)
                except:
                    pass
            return False
    
    def prompt_user_for_update(self, latest_version, download_url):
        """
        Show dialog asking user if they want to update
        Returns: bool - Whether to proceed with update
        """
        # Create a temporary root window for the dialog
        root = tk.Tk()
        root.withdraw()
        
        message = (f"A new version is available!\n\n"
                  f"Current version: {self.current_version}\n"
                  f"Latest version: {latest_version}\n\n"
                  f"Would you like to download and install the update now?\n"
                  f"The application will restart automatically.")
        
        result = messagebox.askyesno(
            "Update Available",
            message,
            icon='info'
        )
        
        root.destroy()
        return result


def check_and_update():
    """
    Main function to check for updates and handle the update process
    Returns: bool - True if update is being installed (app should exit)
    """
    updater = AutoUpdater()
    
    print(f"Checking for updates... (Current version: {updater.current_version})")
    update_available, latest_version, download_url = updater.check_for_updates()
    
    if update_available and download_url:
        print(f"Update available: {latest_version}")
        
        # Ask user if they want to update
        if updater.prompt_user_for_update(latest_version, download_url):
            # Download and install
            if updater.download_and_install_update(download_url, latest_version):
                # Update is being installed, app should exit
                return True
            else:
                # Show error message
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror(
                    "Update Failed",
                    "Failed to download or install the update. Please try again later."
                )
                root.destroy()
    else:
        print("No updates available.")
    
    return False
