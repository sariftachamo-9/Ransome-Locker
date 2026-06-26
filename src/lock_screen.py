"""
Lock Screen - Full UI, Authentication, Attempt Management
Cooldown, Decoy Passwords, Biometric Simulation
"""

import tkinter as tk
from tkinter import messagebox, ttk
import hashlib
import datetime
import time
import threading
from config import CONFIG
from audio_manager import AudioManager
from vm_detector import VMDetector
from logger import Logger


class LockScreen:
    def __init__(self, root, persistence_manager):
        self.root = root
        self.persistence = persistence_manager
        self.audio = AudioManager()
        self.vm_detector = VMDetector()
        self.logger = Logger()
        
        # State variables
        self.attempts = 0
        self.max_attempts = CONFIG["max_attempts"]
        self.cooldown_duration = CONFIG["cooldown_duration"]
        self.is_cooldown = False
        self.is_unlocked = False
        
        # Password hashes
        self.correct_hash = hashlib.sha256(
            CONFIG["correct_password"].encode()
        ).hexdigest()
        
        # Decoy hashes
        self.decoy_hashes = {}
        for decoy, response in CONFIG["decoy_passwords"].items():
            self.decoy_hashes[hashlib.sha256(decoy.encode()).hexdigest()] = response
        
        # VM detection
        self.in_vm, self.vm_indicators = self.vm_detector.is_running_in_vm()
        if CONFIG["check_vm"] and not self.in_vm:
            self.logger.log("WARNING", "Running on physical machine - USE VM!")
        
        # Domain check
        self.domain = self.check_domain()
        
        # Setup window
        self.setup_window()
        self.create_ui()
        self.setup_bindings()
        
        # Log startup
        self.logger.log("STARTUP", f"VM: {self.in_vm}, Domain: {self.domain}")
        
        # Focus
        self.password_entry.focus_set()
    
    def setup_window(self):
        """Configure full-screen window"""
        self.root.title("🔒 SYSTEM LOCKED")
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)
        self.root.configure(bg='#1a1a2e')
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)
        self.root.grab_set()
    
    def setup_bindings(self):
        """Keyboard shortcuts"""
        self.root.bind('<Escape>', self.safe_exit)
        self.root.bind('<Return>', lambda e: self.attempt_unlock())
    
    def check_domain(self):
        """Check if system is domain-joined"""
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                0, winreg.KEY_READ
            )
            domain, _ = winreg.QueryValueEx(key, "Domain")
            winreg.CloseKey(key)
            return domain if domain else "WORKGROUP"
        except:
            return "WORKGROUP"
    
    def create_ui(self):
        """Build lock screen UI"""
        main_frame = tk.Frame(self.root, bg='#1a1a2e')
        main_frame.pack(expand=True, fill='both')
        
        # ── DISCLAIMER ──
        disclaimer = tk.Frame(main_frame, bg='#e74c3c', height=40)
        disclaimer.pack(fill='x', side='top')
        
        disclaimer_text = "Press ESC to exit"
        if not self.in_vm:
            disclaimer_text += " | ⚠️ RUNNING ON PHYSICAL MACHINE!"
        
        tk.Label(
            disclaimer,
            text=disclaimer_text,
            fg='white',
            bg='#e74c3c',
            font=('Arial', 12, 'bold')
        ).pack(pady=8)
        
        # ── CONTENT ──
        content = tk.Frame(main_frame, bg='#1a1a2e')
        content.pack(expand=True)
        
        # Lock icon
        tk.Label(
            content,
            text="🔒",
            fg='#3498db',
            bg='#1a1a2e',
            font=('Segoe UI', 80)
        ).pack(pady=(30, 10))
        
        # Title
        tk.Label(
            content,
            text="SYSTEM LOCKED",
            fg='white',
            bg='#1a1a2e',
            font=('Segoe UI', 32, 'bold')
        ).pack(pady=5)
        
        tk.Label(
            content,
            text="Administrator authorization required",
            fg='#bdc3c7',
            bg='#1a1a2e',
            font=('Segoe UI', 14)
        ).pack(pady=5)
        
        # Domain
        tk.Label(
            content,
            text=f"🏢 Domain: {self.domain}",
            fg='#f39c12',
            bg='#1a1a2e',
            font=('Segoe UI', 10, 'italic')
        ).pack(pady=5)
        
        # Attempt counter
        self.attempts_label = tk.Label(
            content,
            text=f"Attempts remaining: {self.max_attempts}",
            fg='#e67e22',
            bg='#1a1a2e',
            font=('Segoe UI', 14, 'bold')
        )
        self.attempts_label.pack(pady=10)
        
        # ── BIOMETRIC (Optional) ──
        if CONFIG["show_biometric"]:
            bio_frame = tk.Frame(content, bg='#1a1a2e')
            bio_frame.pack(pady=5)
            
            tk.Label(
                bio_frame,
                text="🔐 Windows Hello",
                fg='#3498db',
                bg='#1a1a2e',
                font=('Segoe UI', 10, 'bold')
            ).pack()
            
            bio_buttons = tk.Frame(bio_frame, bg='#1a1a2e')
            bio_buttons.pack(pady=5)
            
            tk.Button(
                bio_buttons,
                text="👤 Face Recognition",
                command=self.fake_biometric,
                bg='#2c3e50',
                fg='white',
                font=('Segoe UI', 9),
                width=15,
                relief='flat'
            ).pack(side='left', padx=5)
            
            tk.Button(
                bio_buttons,
                text="🖐 Fingerprint",
                command=self.fake_biometric,
                bg='#2c3e50',
                fg='white',
                font=('Segoe UI', 9),
                width=15,
                relief='flat'
            ).pack(side='left', padx=5)
            
            tk.Label(
                bio_frame,
                text="or enter password below:",
                fg='#7f8c8d',
                bg='#1a1a2e',
                font=('Segoe UI', 9)
            ).pack(pady=5)
        
        # ── PASSWORD ──
        entry_frame = tk.Frame(content, bg='#1a1a2e')
        entry_frame.pack(pady=10)
        
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            entry_frame,
            textvariable=self.password_var,
            show='•',
            width=30,
            font=('Segoe UI', 16),
            bg='#2c3e50',
            fg='white',
            insertbackground='white',
            relief='flat',
            highlightthickness=2,
            highlightcolor='#3498db',
            highlightbackground='#34495e'
        )
        self.password_entry.pack(pady=5, ipady=8)
        
        # ── UNLOCK BUTTON ──
        self.unlock_btn = tk.Button(
            content,
            text="🔓 Unlock System",
            command=self.attempt_unlock,
            bg='#27ae60',
            fg='white',
            font=('Segoe UI', 14, 'bold'),
            width=20,
            height=2,
            relief='raised',
            cursor='hand2',
            activebackground='#2ecc71'
        )
        self.unlock_btn.pack(pady=15)
        
        # ── STATUS ──
        self.status_label = tk.Label(
            content,
            text="",
            fg='#f1c40f',
            bg='#1a1a2e',
            font=('Segoe UI', 12)
        )
        self.status_label.pack(pady=10)
        
        # ── COOLDOWN ──
        cooldown_frame = tk.Frame(content, bg='#1a1a2e')
        cooldown_frame.pack(pady=5)
        
        self.cooldown_label = tk.Label(
            cooldown_frame,
            text="",
            fg='#e67e22',
            bg='#1a1a2e',
            font=('Segoe UI', 10)
        )
        self.cooldown_label.pack()
        
        self.cooldown_progress = ttk.Progressbar(
            cooldown_frame,
            length=300,
            mode='determinate',
            maximum=self.cooldown_duration
        )
        self.cooldown_progress.pack(pady=5)
        self.cooldown_progress.pack_forget()
        
        # ── FOOTER ──
        tk.Label(
            content,
            text=f"© {datetime.datetime.now().year} Security Research Lab | Simulation",
            fg='#7f8c8d',
            bg='#1a1a2e',
            font=('Arial', 9)
        ).pack(side='bottom', pady=20)
    
    def attempt_unlock(self):
        """Handle unlock attempts"""
        if self.is_cooldown:
            self.status_label.config(
                text="⏳ System is locked during cooldown. Please wait.",
                fg='#e74c3c'
            )
            return
        
        password = self.password_entry.get()
        self.logger.log("ATTEMPT", f"Password entered (length: {len(password)})")
        
        entered_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # ── CHECK DECOY ──
        if entered_hash in self.decoy_hashes:
            response = self.decoy_hashes[entered_hash]
            self.logger.log("DECOY", f"Decoy used: {password} -> {response}")
            
            if password == "kill":
                self.status_label.config(text="🛑 Self-destruct initiated...", fg='#e74c3c')
                self.self_destruct()
            elif password == "reset":
                self.status_label.config(text="🔄 Rebooting system...", fg='#f39c12')
                self.reboot_system()
            else:
                self.unlock_system(decoy=True)
            return
        
        # ── CHECK CORRECT ──
        if entered_hash == self.correct_hash:
            self.logger.log("SUCCESS", f"Correct after {self.attempts} attempts")
            self.unlock_system(decoy=False)
            return
        
        # ── INCORRECT ──
        self.attempts += 1
        remaining = self.max_attempts - self.attempts
        
        self.attempts_label.config(text=f"Attempts remaining: {remaining}")
        self.password_var.set("")
        self.password_entry.focus_set()
        
        self.audio.play_error()
        self.password_entry.config(highlightcolor='#e74c3c')
        self.root.after(500, lambda: self.password_entry.config(highlightcolor='#3498db'))
        
        self.logger.log("FAILURE", f"Attempt #{self.attempts}, {remaining} remaining")
        
        if remaining <= 0:
            self.status_label.config(
                text="⚠️ MAX ATTEMPTS EXCEEDED! INITIATING SYSTEM SHUTDOWN...",
                fg='#e74c3c'
            )
            self.unlock_btn.config(state='disabled', bg='#c0392b')
            self.audio.play_warning()
            self.root.after(2000, self.trigger_shutdown)
        else:
            self.status_label.config(
                text=f"❌ Incorrect password. {remaining} attempt(s) remaining.",
                fg='#e74c3c'
            )
            if remaining == 1:
                self.start_cooldown()
    
    def start_cooldown(self):
        """Start cooldown timer after 2nd attempt"""
        self.is_cooldown = True
        self.cooldown_progress.pack()
        self.cooldown_label.config(text=f"⏳ System locked for {self.cooldown_duration} seconds")
        self.password_entry.config(state='disabled')
        self.unlock_btn.config(state='disabled')
        
        self.logger.log("COOLDOWN", f"Started {self.cooldown_duration}s cooldown")
        
        self.cooldown_remaining = self.cooldown_duration
        self.update_cooldown()
    
    def update_cooldown(self):
        """Update cooldown progress bar"""
        if self.cooldown_remaining > 0:
            self.cooldown_progress['value'] = self.cooldown_duration - self.cooldown_remaining
            self.cooldown_label.config(
                text=f"⏳ System locked for {self.cooldown_remaining} seconds"
            )
            self.cooldown_remaining -= 1
            self.root.after(1000, self.update_cooldown)
        else:
            self.is_cooldown = False
            self.cooldown_progress.pack_forget()
            self.cooldown_label.config(text="")
            self.password_entry.config(state='normal')
            self.unlock_btn.config(state='normal')
            self.password_entry.focus_set()
            self.status_label.config(
                text="✅ Cooldown complete. You may try again.",
                fg='#2ecc71'
            )
            self.logger.log("COOLDOWN", "Cooldown complete")
            self.root.after(2000, lambda: self.status_label.config(text=""))
    
    def trigger_shutdown(self):
        """Trigger shutdown with BSOD"""
        self.logger.log("SHUTDOWN", "Triggering system shutdown")
        from bsod_manager import BSODManager
        bsod = BSODManager(self.root)
        bsod.show()
        self.root.after(5000, self.execute_shutdown)
    
    def execute_shutdown(self):
        """Execute system shutdown"""
        self.logger.log("SHUTDOWN_EXECUTED", "System shutting down")
        self.status_label.config(text="⏳ SHUTTING DOWN...", fg='#e74c3c')
        self.root.update()
        import os
        os.system(f"shutdown /s /t {CONFIG['shutdown_delay']} /c \"Security violation detected\"")
    
    def unlock_system(self, decoy=False):
        """Unlock system and remove persistence"""
        self.is_unlocked = True
        self.logger.log("UNLOCK", f"Decoy: {decoy}")
        self.status_label.config(
            text="✅ Authorization successful! Unlocking...",
            fg='#2ecc71'
        )
        self.audio.play_success()
        self.root.update()
        self.persistence.remove_all()
        self.logger.log("PERSISTENCE_REMOVED", "All persistence removed")
        summary = (
            f"🔓 System Unlocked!\n\n"
            f"Study Data:\n"
            f"• Total attempts: {self.attempts}\n"
            f"• Decoy used: {decoy}\n"
            f"• Time locked: {self.get_time_locked()}\n"
            f"• VM detected: {self.in_vm}\n\n"
            f"Log file: {CONFIG['log_file']}\n"
            ""
        )
        messagebox.showinfo("🔓 Unlocked", summary)
        self.safe_exit()
    
    def self_destruct(self):
        """Remove all persistence and exit"""
        self.logger.log("SELF_DESTRUCT", "Self-destruct initiated")
        self.persistence.remove_all()
        messagebox.showinfo(
            "🛑 Self-Destruct",
            "All persistence removed.\nSystem will now exit."
        )
        self.safe_exit()
    
    def reboot_system(self):
        """Force system reboot"""
        self.logger.log("REBOOT", "Reboot triggered by decoy")
        import os
        os.system("shutdown /r /t 5 /c \"Rebooting...\"")
        self.safe_exit()
    
    def fake_biometric(self):
        """Fake biometric authentication"""
        self.logger.log("BIOMETRIC", "Fake biometric attempt")
        self.status_label.config(
            text="🔍 Scanning... Failed. Please use password.",
            fg='#e74c3c'
        )
        self.audio.play_error()
        self.root.after(2000, lambda: self.status_label.config(text=""))
    
    def get_time_locked(self):
        """Calculate time locked"""
        try:
            diff = datetime.datetime.now() - self.start_time
            minutes = diff.seconds // 60
            seconds = diff.seconds % 60
            return f"{minutes}m {seconds}s"
        except:
            return "Unknown"
    
    def safe_exit(self, event=None):
        """Clean exit"""
        try:
            self.root.grab_release()
        except:
            pass
        self.root.quit()
        self.root.destroy()
