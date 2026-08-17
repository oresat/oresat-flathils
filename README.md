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

A "test harness" is a collection of configuration and tests for the OreSat satellite subject under test (SUT). An example harness is provided to demonstrate the structure of a test harness and can be run witht he following command.

```sh
flathils test example-harness
```

You can look at all availible harnesses with the following command.

```sh
flathils list harnesses
```

Some harnesses may have extra arguments that are only used by them, you can see them using this command.

```sh
flathilts list-args exmaple-harness
```

If you find yourself needing to command pytest directly, you can pass options and arguments through `flathils` to pytest with the `--pytest-args` flag.

You can see what harnesses are availible and what they can do on [Harnesses](docs/harnessses.md)

## Tests

This project uses [Pytest](https://docs.pytest.org/en/stable/index.html).  To run this software's test suite:

```sh
pytest tests/
```
