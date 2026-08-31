# Harnesses

This document lists all the HIL harnesses and what they do.

Index:
- [Example harness](#example-harness)
- [CAN Harnesses](#can-harnesses)

## Example harness

This harness is purely for example purposes, and just shows the concept of HIL testing in FlatHILS

A "test harness" is a collection of configuration and tests for the OreSat satellite subject under test (SUT). An example harness is provided to demonstrate the structure of a test harness and can be run with the following command.

```sh
flathils test example-harness
```

You can run Hardware-in-Loop tests with the `--run-hil` flag:

```sh
flathils test example-harness --run-hil
```

If you find yourself needing to command pytest directly, you can pass options and arguments through `flathils` to pytest with the `--pytest-args` flag.

```sh
# run the example harness and set pytest to verbose.
flathils test example-harness --pytest-args -v
```

## CAN Harnesses

These harnesses use a CAN connection to Communicate primarily with Oresat NXP MCXN947 cards.

> **NOTE:** For all CAN harnesses, make sure you have CAN enabled on your project!

Index:
- [CAN-Harness](#CAN-harness)
  - [Arguments for CAN-harness](#arguments-for-can-harness)
- [Bootloader-harness](#bootloader-harness)
  - [Arguments for bootloader-harness](#arguments-for-bootloader-harness)

### CAN-harness

Verifies that OreSat cards using the NXP MCXN947 SoC are correctly reachable over SocketCAN using CANopen.

1. First, make sure you have a CAN connection with your device as `can0` if you do not have this, see [CAN Adapter Setup](../util/can_udev.md) for setup.

2. Run a CAN harness test to ensure everything works:

```sh
flathils test can-harness --run-hil --pytest-args "--can-device can0 -v"
```
#### Arguments for CAN-harness

- **`--can-device <str>`**  
  **(Required)**: CAN device to be tested, default: `can0`

### Bootloader-harness

Verifies that OreSat cards running the NXP MCXN947 SoC can flash a Zephyr image over CAN using CANopen.

1. First, make sure you have a CAN connection with your device as `can0` if you do not have this, see [CAN Adapter Setup](../util/can_udev.md) for setup. your CAN device can be named anything.

2. Find the path to your zephyr binary file when built. this is typically located in: `~/path/to/build/{APPLICATION}/zephyr/zephyr.signed.bin` where `{APPLICATION}` is the name of your app.

3. Run a flashing test to ensure you can flash images.

```sh
flathils test bootloader-harness --run-hil --pytest-args "--can-device can0 --image-path ~/path/to/zephyr.signed.bin"
```
#### Arguments for bootloader-harness:

- **`--can-device <str>`**  
  **(Required)**: CAN device to be tested, default: `can0`

- **`--image-path <str>`**  
  **(Required)**: Path to Zephyr image to flash, default: `None`

- **`--throttle-delay <float>`**  
  Time to throttle CAN data packets, default: `0`
  
- **`--confirm-image`**  
  Enables Zephyr's image confirmation, default: `False`

- **`--request-crc`**
  Enables Zephyr's CRC image checking, default: `False`
