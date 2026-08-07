# Setting A Udev rule for USB-CAN Adapters

This document covers a one-time setup to make a CAN-to-USB adapter
automatically appear as a SocketCAN interface, so you don't need to bring
it up manually every session.

<<<<<<< Updated upstream
> [!NOTE]
> If you are running candlelight firmware or an equivalent on your adapter, you may skip all of this. Everything should already be set up.

## Prerequisites
=======
> [!IMPORTANT]
> If you have a USB-CAN Adapter with the candlelight firmware, you should not have to do this.

### Prerequisites
>>>>>>> Stashed changes

  1. `can-utils` installed
  2. A USB-CAN adapter (this tutorial uses a Copperforge VulCAN)
  3. A Linux system

It is important to Update `ATTRS{idVendor} / ATTRS{idProduct}` in `99-flathils-can.rules` to match the your adapter's USB ID if not using a VulCAN.

## Installing

> [!WARNING]
> It is recomended to use a Linux-based OS installed on the device itself.

First, open a terminal and make sure you're in `/path/to/oresat-flathils/util`.

Copy and paste the following commands into your terminal:

```sh
sudo cp udev/99-flathils-can.rules /etc/udev/rules.d/
sudo cp systemd/slcand@.service /etc/systemd/system/
sudo udevadm control --reload-rules
sudo systemctl daemon-reload
```

Then unplug and replug the adapter.

### Uninstalling

```sh
sudo systemctl stop slcand@can0.service
sudo rm /etc/udev/rules.d/99-flathils-can.rules
sudo rm /etc/systemd/system/slcand@.service
sudo udevadm control --reload-rules
sudo systemctl daemon-reloadk
```

## Verifying it works

Run the following commands:

```sh
<<<<<<< Updated upstream
ls -l /dev/can0
=======
ls -la /dev/can0
>>>>>>> Stashed changes
systemctl status slcand@can0.service
ip link show can0
```

You should see the symlink pointing at the adapter's tty device:

```sh
lrwxrwxrwx. 1 root root 7 Jul 31 16:31 /dev/can0 -> ttyACM0
```

The service should show `Active: active (running)`:

```sh
● slcand@can0.service - Manages slcand for can0
     Loaded: loaded (/etc/systemd/system/slcand@.service; static)
    Drop-In: /usr/lib/systemd/system/service.d
             └─10-timeout-abort.conf
     Active: active (running) since Fri 2026-07-31 16:31:08 PDT; 20min ago
 Invocation: 7b85ba083634486e85c10ec689473d37
    Process: 127076 ExecStartPost=/usr/sbin/ip link set can0 up (code=exited, status=0/SUCCESS)
   Main PID: 127075 (slcand)
      Tasks: 1 (limit: 18707)
     Memory: 228K (peak: 2.2M)
        CPU: 71ms
     CGroup: /system.slice/system-slcand.slice/slcand@can0.service
             └─127075 /usr/bin/slcand -F -o -c -s8 -t hw -S 3000000 /dev/can0 can0

Jul 31 16:31:08 fedora systemd[1]: Starting slcand@can0.service - Manages slcand for can0...
Jul 31 16:31:08 fedora systemd[1]: Started slcand@can0.service - Manages slcand for can0.
```

And the interface should show up as `link/can`:

```sh
can0: <NOARP,UP,LOWER_UP> mtu 16 qdisc pfifo_fast state UP mode DEFAULT group default qlen 10
    link/can
```

## Troubleshooting

**`ls -l /dev/can0` shows nothing after installing the rule:**

<<<<<<< Updated upstream
Reloading udev rules does not apply to devices already plugged in. Physically unplug and
replug the adapter.
=======
Check for a hyphen in the symlink/instance name. systemd auto-generates a
`.device` unit for every device node by escaping its path, and a literal
`-` in the name itself is ambiguous with that escaping, it can cause
systemd to derive the wrong unit name entirely. Avoid hyphens in the value
passed to `SYMLINK+=` and the systemd instance name; this is why the rule
uses `can0`, not `flathils-can0`.

**`ls -la /dev/can0` shows nothing after installing the rule:**

The rule only fires on `ACTION=="add"`. Reloading udev rules does not
apply to devices already plugged in. Physically unplug and
replug the adapter. To confirm the rule is even being evaluated:
```sh
udevadm test $(udevadm info -q path -n /dev/ttyACM0) 2>&1 | grep -i flathils
```

**Interface exists but stays `state DOWN` and no traffic flows.**

Confirm `ExecStartPost=/usr/sbin/ip link set %i up` is present in the
installed `/etc/systemd/system/slcand@.service` as `slcand` creates the
netdev but does not bring it up on its own.
>>>>>>> Stashed changes

**Adapter isn't detected by the udev rule at all.**

Confirm the VID/PID match if using a different USB-CAN Adapter:

```sh
lsusb | grep -i ad50
```

and compare against `ATTRS{idVendor}` / `ATTRS{idProduct}` in
`99-flathils-can.rules`.
