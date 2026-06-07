# OreSat FlatHILS

The Hardware-in-the-Loop testing software infrastructure for OreSat.

## Overview

OreSat FlatHILS is a software-based testing orchestrator platform for the Portland State Aerospace Society (PSAS) CubeSat called OreSat -- Oregon's First Satellite.

## Up and Running

```sh
python -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
```

### CLI

```sh
flathils -h
```

### Running Test Harnesses

```sh
flathils test --harness example-harness
```
