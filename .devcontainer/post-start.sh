#!/bin/bash

# Run tests
export OTEL_SERVICE_NAME=codespace-platform
export PYTEST_RUN_NAME=startup-automated-test
export OTEL_EXPORTER_OLTP_ENDPOINT=http://localhost:4317
#pytest --export-traces startup_test.py
pytest --export-traces startup_test.py