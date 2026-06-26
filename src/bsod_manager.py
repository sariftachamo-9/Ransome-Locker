"""
BSOD Manager - Fake Blue Screen of Death
"""

import tkinter as tk
from tkinter import ttk


class BSODManager:
    def __init__(self, root):
        self.root = root
    
    def show(self):
        """Display fake BSOD"""
        bsod = tk.Toplevel(self.root)
        bsod.title("Blue Screen")
        bsod.attributes('-fullscreen', True)
        bsod.attributes('-topmost', True)
        bsod.configure(bg='#0000aa')
        bsod.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # Sad face
        tk.Label(
            bsod,
            text=":(",
            fg='white',
            bg='#0000aa',
            font=('Segoe UI', 72, 'bold')
        ).pack(pady=(50, 20))
        
        # Error text
        error_text = (
            "Your PC ran into a problem and needs to restart.\n"
            "We're just collecting some error info, and then we'll restart for you.\n\n"
            "SECURITY_VIOLATION_DETECTED\n\n"
            "What failed: winlogon.exe\n"
            "Error code: 0xC0000221 (0x00000000)\n"
            "Physical memory dump progress: 100%\n\n"
            "Contact your system administrator if this problem persists.\n\n"
            ""
            "No real damage occurred."
        )
        tk.Label(
            bsod,
            text=error_text,
            fg='white',
            bg='#0000aa',
            font=('Consolas', 14),
            justify='left'
        ).pack(pady=20)
        
        # Progress bar
        progress = ttk.Progressbar(
            bsod,
            length=500,
            mode='indeterminate'
        )
        progress.pack(pady=20)
        progress.start(50)
        
        self.bsod_window = bsod
        self.root.update()
