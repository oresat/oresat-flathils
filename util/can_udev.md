# CAN Adapter setup

This document covers a one-time setup to make a CAN-to-USB adapter
automatically appear as a SocketCAN interface, so you don't need to bring
it up manually every session.

### Prerequisites

  1. `can-utils` installed
  2. A USB-CAN adapter (this tutorial uses a Copperforge VulCAN)
  3. A Linux system 

It is important to Update `ATTRS{idVendor} / ATTRS{idProduct}` in `99-flathils-can.rules` to match the your adapter's USB ID if not using a VulCAN.

## udev

> [!WARNING]
> This requires a Linux-based OS installed on the device itself. VMs and
> WSL users may have trouble passing through USB-CAN adapters for HIL
> tests.

First, open a terminal and make sure you're in `/path/to/oresat-flathils/util`.

Copy and paste the following commands into your terminal:

```sh
sudo cp udev/99-flathils-can.rules /etc/udev/rules.d/
sudo cp systemd/slcand@.service /etc/systemd/system/
sudo udevadm control --reload-rules
sudo systemctl daemon-reload
```

Then unplug and replug the adapter. A physical replug is required the
first time as reloading udev rules alone does not apply
`ACTION=="add"` rules to devices that are already connected.

### Uninstalling

```sh
sudo systemctl stop slcand@flathilscan0.service
sudo rm /etc/udev/rules.d/99-flathils-can.rules
sudo rm /etc/systemd/system/slcand@.service
sudo udevadm control --reload-rules
sudo systemctl daemon-reload
```

## Verifying it works

Run the following commands:

```sh
ls -la /dev/flathilscan0
systemctl status slcand@flathilscan0.service
ip link show flathilscan0
```

You should see the symlink pointing at the adapter's tty device:

```sh
lrwxrwxrwx. 1 root root 7 Jul 31 16:31 /dev/flathilscan0 -> ttyACM0
```

The service should show `Active: active (running)`:

```sh
● slcand@flathilscan0.service - Manages slcand for flathilscan0
     Loaded: loaded (/etc/systemd/system/slcand@.service; static)
    Drop-In: /usr/lib/systemd/system/service.d
             └─10-timeout-abort.conf
     Active: active (running) since Fri 2026-07-31 16:31:08 PDT; 20min ago
 Invocation: 7b85ba083634486e85c10ec689473d37
    Process: 127076 ExecStartPost=/usr/sbin/ip link set flathilscan0 up (code=exited, status=0/SUCCESS)
   Main PID: 127075 (slcand)
      Tasks: 1 (limit: 18707)
     Memory: 228K (peak: 2.2M)
        CPU: 71ms
     CGroup: /system.slice/system-slcand.slice/slcand@flathilscan0.service
             └─127075 /usr/bin/slcand -F -o -c -s8 -t hw -S 3000000 /dev/flathilscan0 flathilscan0

Jul 31 16:31:08 fedora systemd[1]: Starting slcand@flathilscan0.service - Manages slcand for flathilscan0...
Jul 31 16:31:08 fedora systemd[1]: Started slcand@flathilscan0.service - Manages slcand for flathilscan0.
```

And the interface should show up as `link/can`:

```sh
flathilscan0: <NOARP,UP,LOWER_UP> mtu 16 qdisc pfifo_fast state UP mode DEFAULT group default qlen 10
    link/can
```

CAN interfaces are sometimes shown as `state UNKNOWN` rather than `UP`,
this is normal, since CAN has no carrier-detect concept the way Ethernet
does. What matters is that the service is running and the interface
exists.

## Troubleshooting

**`slcand@....service` fails with "Bound to unit dev-....device, but unit isn't active" / dependency timeouts:**

Check for a hyphen in the symlink/instance name. systemd auto-generates a
`.device` unit for every device node by escaping its path, and a literal
`-` in the name itself is ambiguous with that escaping, it can cause
systemd to derive the wrong unit name entirely. Avoid hyphens in the value
passed to `SYMLINK+=` and the systemd instance name; this is why the rule
uses `flathilscan0`, not `flathils-can0`.

**`ls -la /dev/flathilscan0` shows nothing after installing the rule:**

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

**Adapter isn't detected by the udev rule at all.**

Confirm the VID/PID match:
```sh
lsusb | grep -i ad50
```
and compare against `ATTRS{idVendor}` / `ATTRS{idProduct}` in
`99-flathils-can.rules`.
