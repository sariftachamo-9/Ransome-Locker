"""
VM Detector - Detect virtual machine environment
"""

import uuid
import platform
import subprocess


class VMDetector:
    def is_running_in_vm(self):
        """Check for VM indicators"""
        indicators = []
        
        # MAC address check
        try:
            mac = uuid.getnode()
            mac_hex = f"{mac:012x}".upper()
            vm_macs = {
                "000C29": "VMware",
                "080027": "VirtualBox",
                "00155D": "Hyper-V",
                "000569": "VMware",
                "005056": "VMware"
            }
            for prefix, name in vm_macs.items():
                if mac_hex.startswith(prefix):
                    indicators.append(name)
        except:
            pass
        
        # Process check
        try:
            vm_processes = ["VBoxService.exe", "VMwareService.exe", "vmtoolsd.exe", "VBoxTray.exe", "VMwareTray.exe"]
            result = subprocess.run('tasklist', shell=True, capture_output=True)
            output = result.stdout.decode().lower()
            for proc in vm_processes:
                if proc.lower() in output:
                    indicators.append(proc.replace('.exe', ''))
        except:
            pass
        
        # System info
        try:
            sys_info = platform.platform().lower()
            if "virtualbox" in sys_info or "vmware" in sys_info:
                indicators.append("SystemInfo")
        except:
            pass
        
        return len(indicators) > 0, indicators
