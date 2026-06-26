"""
Main entry point for Lock Screen Simulator
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

from config import CONFIG
from persistence_manager import PersistenceManager
from lock_screen import LockScreen
from logger import Logger


def main():
    """Run the lock screen simulation.
    Requires the presence of the safety flag file `educational_simulation.txt`
    in the project root. If the file is missing, the user is prompted to
    confirm they are running in an isolated VM.
    """
    # Safety check
    safety_file = os.path.join(os.path.dirname(__file__), '..', 'educational_simulation.txt')
    safety_file = os.path.abspath(safety_file)
    if not os.path.exists(safety_file):
        response = messagebox.askyesno(
            "⚠️ SAFETY CHECK",
            "This is an EDUCATIONAL SIMULATION.\n\n"
            "Are you running this in an isolated Virtual Machine?\n\n"
            "Create a file named 'educational_simulation.txt' in the project root to bypass this warning."
        )
        if not response:
            sys.exit(0)

    # Initialize GUI root
    root = tk.Tk()
    script_path = os.path.abspath(__file__)
    persistence = PersistenceManager(script_path)

    # Install or repair persistence mechanisms
    installed = persistence.check_installed()
    if not any(installed.values()):
        persistence.install_all()
    else:
        persistence.verify_and_repair()

    # Launch the lock screen UI
    try:
        app = LockScreen(root, persistence)
        root.mainloop()
    except Exception as e:
        Logger().log("ERROR", f"Fatal error: {e}")
        messagebox.showerror("Error", f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

