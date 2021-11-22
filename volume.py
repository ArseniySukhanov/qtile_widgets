import os
import subprocess

from libqtile import bar, images
from libqtile.widget import base


class Volume(base._TextBox, base.MarginMixin):
    """
    Widget which shows modern volume
    """
    orientations = base.ORIENTATION_HORIZONTAL
    defaults = [
        ('update_interval', 0.2, 'Seconds between status updates'),
    ]

    def __init__(self, **config):
        base._TextBox.__init__(self, "0", width=bar.CALCULATED, **config)
        self.add_defaults(Volume.defaults)
        self.add_defaults(base.MarginMixin.defaults)
        self._variable_defaults["margin"] = 0
        self.length_type = bar.STATIC
        self.length = 0
        self.surfaces = {}
        self.theme_path = os.path.join(os.path.expanduser('~'),
                                       '.config/qtile/widgets/volume/')

    def timer_setup(self):
        self.setup_images()
        self.update()
        self.timeout_add(self.update_interval, self.update)

    def update(self):
        self.bar.draw()
        self.timeout_add(self.update_interval, self.update)

    def get_volume(self):

        mute = str(subprocess.run(['pamixer', '--get-mute'],
                                  stdout=subprocess.PIPE).stdout)[:-1]
        if "true" in mute:
            return None
        else:
            volume = int(
                str(subprocess.run(['pamixer', '--get-volume'],
                                   stdout=subprocess.PIPE).stdout)[2:-3])
            return volume
        return None

    def setup_images(self):
        names = (
            'volume_off',
            'volume_low',
            'volume_medium',
            'volume_high'
        )
        d_images = images.Loader(self.theme_path)(*names)
        for name, img in d_images.items():
            new_height = self.bar.height - 2 * self.margin_y
            img.resize(height=new_height)
            if img.width > self.length:
                self.length = img.width + self.margin_y
            self.surfaces[name] = img.pattern

    def draw(self):
        self.volume = self.get_volume()
        self.drawer.clear(self.background or self.bar.background)
        if (self.volume is None) or (self.volume == 0):
            img_name = 'volume_off'
        elif self.volume <= 30:
            img_name = 'volume_low'
        elif self.volume < 80:
            img_name = 'volume_medium'
        else:
            img_name = 'volume_high'
        self.drawer.ctx.save()
        self.drawer.ctx.translate(self.margin_x, self.margin_y)
        self.drawer.ctx.set_source(self.surfaces[img_name])
        self.drawer.ctx.paint()
        self.drawer.draw(offsetx=self.offset, offsety=self.offsety,
                         width=self.length)
