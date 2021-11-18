import os
from typing import NamedTuple, Optional

from enum import Enum, unique
from libqtile import configurable
from libqtile.log_utils import logger
from libqtile.widget import base


@unique
class BatteryState(Enum):
    CHARGING = 1
    DISCHARGING = 2
    FULL = 3
    EMPTY = 4


BatteryStatus = NamedTuple("BatteryStatus", [
    ("state", BatteryState),
    ("percent", float),
])


class _Battery(configurable.Configurable):
    defaults = [
        (
            'status_file',
            None,
            'Name of status file in \
            /sys/class/power_supply/battery_name'
        ),
        (
            'energy_now_file',
            None,
            'Name of the file with the current energy in \
            /sys/class/power_supply/battery_name'
        ),
        (
            'energy_full_file',
            None,
            'Name of file with the maximum energy in \
            /sys/class/power_supply/battery_name'
        )
    ]

    filenames = {}

    BAT_DIR = '/sys/class/power_supply'

    BATTERY_INFO_FILES = {
        'energy_now_file': ['charge_now'],
        'energy_full_file': ['charge_full'],
        'status_file': ['status'],
    }

    def __init__(self, **config):
        _Battery.defaults.append(('battery',
                                  self._get_battery_name(),
                                  'ACPI name of a battery, usually BAT0'))

        configurable.Configurable.__init__(self, **config)
        self.add_defaults(_Battery.defaults)
        if isinstance(self.battery, int):
            self.battery = "BAT{}".format(self.battery)

    def _get_battery_name(self):
        if os.path.isdir(self.BAT_DIR):
            bats = [f for f in os.listdir(self.BAT_DIR) if f.startswith('BAT')]
            if bats:
                return bats[0]
        return 'BAT0'

    def _load_file(self, name) -> Optional[str]:
        path = os.path.join(self.BAT_DIR, self.battery, name)
        try:
            with open(path, 'r') as f:
                return f.read().strip()
        except OSError as e:
            logger.debug("Failed to read '{}': {}".format(path, e))
            if isinstance(e, FileNotFoundError):
                return None
            return "-1"

    def _get_param(self, name) -> str:
        if name in self.filenames and self.filenames[name]:
            result = self._load_file(self.filenames[name])
            if result is not None:
                return result

        file_list = self.BATTERY_INFO_FILES.get(name)[:]
        user_file_name = getattr(self, name, None)
        if user_file_name is not None:
            file_list.insert(0, user_file_name)

        for filename in file_list:
            value = self._load_file(filename)
            if value is not None:
                self.filenames[name] = filename
                return value

            raise RuntimeError("Unable to read status for {}".format(name))

    def update_status(self) -> BatteryStatus:
        stat = self._get_param('status_file')

        if stat == "Full":
            state = BatteryState.FULL
        elif stat == "Charging":
            state = BatteryState.CHARGING
        else:
            state = BatteryState.DISCHARGING

        now_str = self._get_param('energy_now_file')
        full_str = self._get_param('energy_full_file')

        now = float(now_str)
        full = float(full_str)

        if full == 0:
            percent = 0.
        else:
            percent = now / full

        return BatteryStatus(state=state, percent=percent)


def load_battery(**config) -> _Battery:
    """Default battery loading function

    Loads and returns the _Battery interface

    Parameters
    ----------
    config: Dictionary of config options that are passed to the generated
    battery

    Return
    ------
    The configured _Battery for the current platform.
    """
    return _Battery(**config)


class batteryNerdIcon(base.ThreadPoolText):
    """battery monitoring widget with Nerd Icons"""
    orientations = base.ORIENTATION_HORIZONTAL
    defaults = [
       ('low_percentage', 0.10, 'Indicates when to use low foreground'),
       ('low_foreground', 'FF0000', 'Font color on low battery'),
       ('update_interval', 60, 'Seconds between status updates'),
       ('battery', 0, 'Which battery should be monitored')
    ]

    def __init__(self, **config) -> None:

        base.ThreadPoolText.__init__(self, "", **config)
        self.add_defaults(self.defaults)

        self._battery = self._load_battery(**config)

    @staticmethod
    def _load_battery(**config):
        return load_battery(**config)

    def poll(self) -> str:
        """Determine the text to display

        Function returning a string with battery information to display on the
        status bar
        """
        try:
            status = self._battery.update_status()
        except RuntimeError as e:
            return 'Error: {}'.format(e)

        return self.build_string(status)

    def build_string(self, status: BatteryStatus) -> str:
        """Determine the string to return for the given battery state

        Parameters
        ----------
        status:
            The current status of the battery

        Returns
        -------
        str
            The string to display for the current status
        """
        def get_percent_icon_ch(perc):
            return {
                perc <= 0.25: "",
                0.25 < perc <= 0.35: "",
                0.35 < perc <= 0.55: "",
                0.55 < perc <= 0.70: "",
                0.70 < perc <= 0.85: "",
                0.85 < perc <= 0.95: "",
                0.95 < perc: ""
            }[True]

        def get_percent_icon_unch(perc):
            return {
                perc <= 0.5: "",
                0.5 < perc <= 0.15: "",
                0.15 < perc <= 0.25: "",
                0.25 < perc <= 0.35: "",
                0.35 < perc <= 0.45: "",
                0.45 < perc <= 0.55: "",
                0.55 < perc <= 0.65: "",
                0.65 < perc <= 0.75: "",
                0.75 < perc <= 0.85: "",
                0.85 < perc <= 0.95: "",
                0.95 < perc: ""
            }[True]

        if self.layout is not None:
            if status.state == BatteryState.DISCHARGING \
                    and status.percent < self.low_percentage:
                self.layout.colour = self.low_foreground
            else:
                self.layout.colour = self.foreground

        if status.state == BatteryState.FULL:
            return ""
        if status.state == BatteryState.CHARGING:
            return get_percent_icon_ch(status.percent)
        else:
            return get_percent_icon_unch(status.percent)
