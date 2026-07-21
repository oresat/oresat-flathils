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
    python -m pip install -e .
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

If you find yourself needing to command pytest directly, you can pass options and arguments through `flathils` to pytest with the `--pytest_args` flag.

```sh
# run the example harness and set pytest to verbose.
flathils test example-harness --pytest_args -v
```

## CAN Harness

> [!WARNING]  
> Your prj.conf for your build **MUST** have the CAN app enabled, if not you will fail every test.

Verifies that OreSat cards using the NXP MCXN947 SoC are
correctly reachable over CANopen via a Vulcan USB to CAN adapter. This checks:

1. The node produces a CANopen heartbeat message on the bus.
2. The Program Software ID object (`0x1F56`) is readable, confirming the
   SDO server is responding and the application-level OD is populated.
3. The Program Software ID object correctly rejects writes (abort code
   `0x06010002`), confirming it's implemented as read-only on-device.

Requires a Copperforge Vulcan connected via USB. Other USB-CAN adapters
may work but will require editing the `ID_VENDOR_ID`/`ID_MODEL_ID` match
in `env.yaml` (use `lsusb` on linux) to your adapter's USB IDs — use at your own risk.


    pytest -v --run-hil --lg-env src/oresat_flathils/harnesses/vulcan_harness/env.yaml \
        src/oresat_flathils/harnesses/vulcan_harness/test_canbus.py


## Tests

This project uses [Pytest](https://docs.pytest.org/en/stable/index.html).  To run this software's test suite:

```sh
pytest tests/
```
