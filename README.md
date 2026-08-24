# OreSat FlatHILS

The Hardware-in-the-Loop testing software infrastructure for OreSat.

## Index

- [Overview](#overview)
- [Up and Running](#up-and-running)
  - [CLI](#cli)
  - [Running Test Harnesses](#running-test-harnesses)
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

A "test harness" is a collection of configuration and tests for the OreSat satellite subject under test (SUT). An example harness is provided to demonstrate the structure of a test harness and can be run with the following command.

```sh
flathils test example-harness
```

If you find yourself needing to command pytest directly, you can pass options and arguments through `flathils` to pytest with the `--pytest-args` flag.

```sh
# run the example harness and set pytest to verbose.
flathils test example-harness --pytest-args -v
```

to test a specific harness see [Harnesses](docs/harnesses.md)

## Tests

This project uses [Pytest](https://docs.pytest.org/en/stable/index.html).  To run this software's test suite:

```sh
pytest tests/
```
