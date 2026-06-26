"""
Logger - JSON logging system
"""

import json
import datetime
import socket
import platform
import os
from config import CONFIG


class Logger:
    def __init__(self):
        self.log_file = CONFIG["log_file"]
        self.system_info = self.get_system_info()
    
    def get_system_info(self):
        """Get system information"""
        return {
            "hostname": socket.gethostname(),
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version()
        }
    
    def log(self, event_type, details):
        """Log event to JSON file"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "event": event_type,
            "details": details,
            "system": self.system_info
        }
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except:
            pass
        
        if CONFIG["enable_network_logging"]:
            self.send_to_server(log_entry)
    
    def send_to_server(self, data):
        """Send log to server (optional)"""
        try:
            import requests
            requests.post(CONFIG["log_server"], json=data, timeout=2)
        except:
            pass
    
    def export_json(self):
        """Export all logs as JSON"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, "r") as f:
                    return [json.loads(line) for line in f if line.strip()]
        except:
            return []
        return []
