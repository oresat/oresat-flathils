"""Configurations for mcuboot harness"""

def pytest_addoption(parser):
    parser.addoption("--use-block-transfer", action="store_true", default=False)