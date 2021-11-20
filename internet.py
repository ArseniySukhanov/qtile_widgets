import iwlib
import subprocess
import math

from libqtile import bar
from libqtile.widget import base


def check_wired():
    """
    Checks if there are working wired connections

    Return:
    0 - there are not wired connections
    >0 - there are some wired connections
    """
    result = subprocess.run('cat /sys/class/net/enp*/carrier', shell=True,
                            stdout=subprocess.PIPE).stdout.splitlines()
    if len(result) == 0:
        return 0
    actual_result = 0
    for _res in result:
        actual_result += int(_res.decode('UTF-8'))
    return actual_result


def get_status(interface_name):
    interface = iwlib.get_iwconfig(interface_name)
    if 'stats' not in interface:
        return None, None
    quality = interface['stats']['quality']
    essid = bytes(interface['ESSID']).decode()
    return essid, quality


def to_rads(degrees):
    return degrees * math.pi / 180.0


class Internet(base._Widget):
    """
    Displays if there is an internet connection, and if it is type of it

    Widget requirements: iwlib_
    """

    orientations = base.ORIENTATION_HORIZONTAL
    defaults = [
        ('interface', 'wlan0', 'The wlan interface to monitor'),
        ('update_interval', 1, 'The update interval')
    ]

    def __init__(self, length=bar.CALCULATED, **config):
        base._Widget.__init__(self, length, **config)
        self.add_defaults(Internet.defaults)

    def timer_setup(self):
        self.draw()
        self.timeout_add(self.update_interval, self.timer_setup)

    def draw_wifi(self, percentage):
        WIFI_HEIGHT = 10
        WIFI_ARC_DEGREES = 80

        y_margin = (self.bar.height - WIFI_HEIGHT) / 2
        half_arc = WIFI_ARC_DEGREES / 2

        # Draw grey background
        self.drawer.ctx.new_sub_path()
        self.drawer.ctx.move_to(WIFI_HEIGHT, y_margin + WIFI_HEIGHT)
        self.drawer.ctx.arc(WIFI_HEIGHT,
                            y_margin + WIFI_HEIGHT,
                            WIFI_HEIGHT,
                            to_rads(270 - half_arc),
                            to_rads(270 + half_arc))
        self.drawer.set_source_rgb("282c34")
        self.drawer.ctx.fill()

        # Draw white section to represent signall strength
        self.drawer.ctx.new_sub_path()
        self.drawer.ctx.move_to(WIFI_HEIGHT, y_margin + WIFI_HEIGHT)
        self.drawer.ctx.arc(WIFI_HEIGHT,
                            y_margin + WIFI_HEIGHT,
                            WIFI_HEIGHT * percentage,
                            to_rads(270 - half_arc),
                            to_rads(270 + half_arc))
        self.drawer.set_source_rgb("abb2bf")
        self.drawer.ctx.fill()

    def calculate_length(self):
        return 16

    def draw(self):
        self.drawer.clear(self.background or self.bar.background)
        wired = check_wired()
        if wired > 0:
            self.layout = self.drawer.textlayout("",
                                                 'abb2bf',
                                                 'sans',
                                                 22,
                                                 None,
                                                 markup=True)
            self.layout.draw(2, 0)
        else:
            essid, quality = get_status(self.interface)
            disconnected = essid is None
            if disconnected:
                self.layout = self.drawer.textlayout("",
                                                     'abb2bf',
                                                     'sans',
                                                     22,
                                                     None,
                                                     markup=True)
                self.layout.draw(2, 0)
            else:
                self.draw_wifi(float(quality/70))
        self.drawer.draw(offsetx=self.offset, offsety=self.offsety,
                         width=self.length)
