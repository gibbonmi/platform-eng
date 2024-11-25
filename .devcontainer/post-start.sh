#!/bin/bash

# Run tests
export PYTEST_RUN_NAME=startup-automated-test
pytest --export-traces startup_test.py