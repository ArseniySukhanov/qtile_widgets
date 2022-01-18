# qtile_widgets
Custom [qtile](https://github.com/qtile/qtile) widgets
## List of widgets
Battery widget

Internet widget

Volume widget

Keyboard layout widget (in order to work need [xkblayout-state](https://github.com/nonpop/xkblayout-state.git))
## Installation
```
git clone https://github.com/ArseniySukhanov/qtile_widgets.git ~/.config/qtile/widgets
```
Afterwards you need to add in your config.py
```
from widgets import name_of_the_widget
```
and
```
name_of_the_widget.name_of_the_widget()
```
inside bar
