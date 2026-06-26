"""
Audio Manager - System sound feedback
"""

import ctypes


class AudioManager:
    def __init__(self):
        try:
            self.user32 = ctypes.windll.user32
        except:
            self.user32 = None
    
    def play_error(self):
        """Play error sound (MB_ICONHAND = 0x10)"""
        if self.user32:
            self.user32.MessageBeep(0x10)
    
    def play_success(self):
        """Play success sound (MB_ICONASTERISK = 0x40)"""
        if self.user32:
            self.user32.MessageBeep(0x40)
    
    def play_warning(self):
        """Play warning sound (MB_ICONWARNING = 0x30)"""
        if self.user32:
            self.user32.MessageBeep(0x30)
