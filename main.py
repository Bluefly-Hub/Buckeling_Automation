"""
Buckeling Automation - Main Entry Point
Author: Brad Smith
Version: 1.0.0
"""
from GUI_Automation import launch_gui
from updater import check_and_update
from version import __version__


def main():
    """Start the automation GUI application"""
    # Check for updates first
    print(f"Buckeling Automation v{__version__}")
    if check_and_update():
        # Update is being installed, exit the application
        return
    
    # Start the GUI
    launch_gui()


if __name__ == "__main__":
    main()
