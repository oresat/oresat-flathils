# OreSat FlatHILS

The Hardware-in-the-Loop testing software infrastructure for OreSat.

## Overview

OreSat FlatHILS is a software-based testing orchestrator platform for the Portland State Aerospace Society (PSAS) CubeSat called OreSat -- Oregon's First Satellite.

## Up and Running

1.  Spin up a [Python virtual environment](https://docs.python.org/3/library/venv.html).

    ```sh
    python -m venv .venv
    source .venv/bin/activate
    ```

2.  Install project dependencies inside the newly-active virtual environment

    ```sh
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install -e . --group-dev
    ```

3.  When you are done developing, deactivate the virtual environment.

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

Verifies that OreSat cards using the NXP MCXN947 SoC are
correctly reachable over SocketCAN using CANopen.

This Requires a Copperforge Vulcan connected via USB. Other USB-CAN adapters
may work but will require editing the `ID_VENDOR_ID`/`ID_MODEL_ID` match
in `env.yaml` (use `lsusb` on linux) to your adapter's USB IDs — use at your own risk.

> [!WARNING]  
> Your zephyr build's `prj.conf` for your build **MUST** have the CAN app enabled, if not you will fail every test. you will also need to enable read/write on your `dev` path.

1. First, make sure you have a CAN connection with your device as `flathilscan0`
if you do not have this, see [CAN Adapter Setup](util/can_udev.md) for setup

2. Run a CAN harness test to ensure everything works:

```sh
flathils test can-harness --run-hil --pytest-args -v
```

## Tests

This project uses [Pytest](https://docs.pytest.org/en/stable/index.html).  To run this software's test suite:

```sh
pytest tests/
```
