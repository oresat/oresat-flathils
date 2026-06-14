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
flathils -h
```

### Running Test Harnesses

A "test harness" is a collection of configuration and tests for the OreSat satellite subject under test (SUT). An example harness is provided to demonstrate the structure of a test harness and can be run witht he following command.

```sh
flathils test --harness example-harness
```

## Tests

This project uses [Pytest](https://docs.pytest.org/en/stable/index.html).  To run this software's test suite:

```sh
pytest tests/
```
