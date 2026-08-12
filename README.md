# OreSat FlatHILS

The Hardware-in-the-Loop testing software infrastructure for OreSat.

## Index

- [Overview](#overview)
- [Up and Running](#up-and-running)
  - [CLI](#cli)
  - [Running Test Harnesses](#running-test-harnesses)
- [CAN Harness](#can-harness)
- [Bootloader Harness](#bootloader-harness)
  - [Aditional arguments for bootloader-harness](#aditional-arguments-for-bootloader-harness)
- [Tests](#tests)

## Overview

OreSat FlatHILS is a software-based testing orchestrator platform for the Portland State Aerospace Society (PSAS) CubeSat called OreSat -- Oregon's First Satellite.

## Up and Running

1. Spin up a [Python virtual environment](https://docs.python.org/3/library/venv.html).

    ```sh
    python -m venv .venv
    source .venv/bin/activate
    ```

2. Install project dependencies inside the newly-active virtual environment

    ```sh
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install -e . --group-dev
    ```

3. When you are done developing, deactivate the virtual environment.

    ```sh
    deactivate
    ```

### CLI

`flathils` cli can be invoked to list the available options using the following command.

```sh
flathils --help
```

### Running Test Harnesses

A "test harness" is a collection of configuration and tests for the OreSat satellite subject under test (SUT). An example harness is provided to demonstrate the structure of a test harness and can be run witht he following command.

```sh
flathils test example-harness
```

If you find yourself needing to command pytest directly, you can pass options and arguments through `flathils` to pytest with the `--pytest-args` flag.

```sh
# run the example harness and set pytest to verbose.
flathils test example-harness --pytest-args -v
```

## CAN Harness

Verifies that OreSat cards using the NXP MCXN947 SoC are correctly reachable over SocketCAN using CANopen.

> **NOTE:** Make sure you have CAN enabled on your project!

1. First, make sure you have a CAN connection with your device as `can0` if you do not have this, see [CAN Adapter Setup](util/can_udev.md) for setup. your CAN device can be named anything.

2. Run a CAN harness test to ensure everything works:

```sh
flathils test can-harness --run-hil --pytest-args "--can-device can0 -v"
```

## Bootloader Harness

Verifies that OreSat cards running the NXP MCXN947 SoC can flash a Zephyr image over CAN using CANopen.

> **NOTE:** Make sure you have CAN enabled on your project!

1. First, make sure you have a CAN connection with your device as `can0` if you do not have this, see [CAN Adapter Setup](util/can_udev.md) for setup. your CAN device can be named anything.

2. Find the path to your zephyr binary file when built. this is typically located in: `~/path/to/build/{APPLICATION}/zephyr/zephyr.signed.bin` where `{APPLICATION}` is the name of your app.

3. Run a flahing test to ensure you can flash images.

```sh
flathils test bootloader-harness --run-hil --pytest-args "--can-device can0 --image-path ~/path/to/zephyr.signed.bin"
```

### Aditional arguments for bootloader-harness

- **`--image-path`**  
  File path to your Zephyr image. Required.

- **`--throttle-delay <float>`**  
  Time to throttle CAN data packets
  
- **`--confirm-image`**  
  Enables Zephyr's image confirmation.

- **`--request-crc`**
  Enables Zephyr's CRC image checking.

## Tests

This project uses [Pytest](https://docs.pytest.org/en/stable/index.html).  To run this software's test suite:

```sh
pytest tests/
```
