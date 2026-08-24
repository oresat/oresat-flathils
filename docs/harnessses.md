# Harnesses

This document lists all HIL harnesses and what they do.

> **NOTE:** For CAN harnesses, make sure you have CAN enabled on your project!

## CAN Harness

Verifies that OreSat cards using the NXP MCXN947 SoC are correctly reachable over SocketCAN using CANopen.

1. First, make sure you have a CAN connection with your device as `can0` if you do not have this, see [Setting up a udev rule](../util/can_udev.md) for setup.

2. Run a CAN harness test to ensure everything works:

```sh
flathils test can-harness --run-hil --pytest-args "--can-device can0 -v"
```

## Bootloader Harness

Verifies that OreSat cards running the NXP MCXN947 SoC can flash a Zephyr image over CAN using CANopen.

1. First, make sure you have a CAN connection with your device as `can0` if you do not have this, see [CAN Adapter Setup](../util/can_udev.md) for setup. your CAN device can be named anything.

2. Find the path to your zephyr binary file when built. this is typically located in: `~/path/to/build/{APPLICATION}/zephyr/zephyr.signed.bin` where `{APPLICATION}` is the name of your app.

3. Run a flashing test to ensure you can flash images.

```sh
flathils test bootloader-harness --run-hil --pytest-args "--can-device can0 --image-path ~/path/to/zephyr.signed.bin"
```

There are additional arguments you can put such as throttle delay, and zephyr checking algorithms, see `flathils harnesses`.
