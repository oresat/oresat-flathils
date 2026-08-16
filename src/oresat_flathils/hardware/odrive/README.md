
You may need to add a udev rule

Do `lsusb` to see if the odrive shows up

Use `lsusb -v` to get the idVendor attribute (typically 1209)

Add the following to `/etc/udev/rules.d` in a file such as `91-odrive.rules`

```
SUBSYSTEM=="usb", ATTR{idVendor}=="1209", ATTR{idProduct}=="0d3[0-9]", MODE="0666", ENV{ID_MM_DEVICE_IGNORE}="1"
SUBSYSTEM=="usb", ATTR{idVendor}=="0483", ATTR{idProduct}=="df11", MODE="0666"
```

For the most up-to-date udev rule, see 

https://gui.odriverobotics.com/configuration

or directly download at

https://cdn.odriverobotics.com/files/odrive-udev-rules.rules


## odrivetool

https://docs.odriverobotics.com/v/latest/interfaces/odrivetool.html

This is a command line tool that has similar functionality to the Web GUI

## High Data Capture rate

The current firmware version (0.6.12) does not have this feature

Updating firmware to at least 1926669f (2026-08-04)

## Configuration

Here is the documentation from loading and saving odrive configurations:

https://docs.odriverobotics.com/v/latest/interfaces/odrivetool.html#configuration-backup
