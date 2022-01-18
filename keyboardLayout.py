import os
import subprocess

from typing import Any, List, Tuple

from libqtile import bar
from libqtile.widget import base

class KeyboardLayout(base.InLoopPollText):
    """Widget which shows current keyboard layout language"""
    defaults = [
        ("font", "sans", "Text font"),
        ("fontsize", None, "Font pixel size. Calculated if None"),
        ("fontshadow", None, "Font shadow color, default is None(no shadow)"),
        ("padding", None, "Padding left and right. Calculated if None"),
        ("foreground", "#ffffff", "Foreground color"),
    ]
    def __init__(self,  width=bar.CALCULATED, **config):
        base.InLoopPollText.__init__(self, width=width, **config)
        self.add_defaults(self.defaults)

    def poll(self) -> str:
        """Determine the text to display
 
        Function returns a string with current layout language
        """
        layout=(str(subprocess.run(['xkblayout-state', 'print', '%s'],stdout=subprocess.PIPE).stdout)[2:-1]).upper()
        return layout
