#!/bin/bash

uv run ruff check --output-format=github .
uv run coverage run -m pytest -v -s
uv run coverage report -m
uv run coverage html
uv run darglint --verbosity 2 --docstring-style sphinx libyamlconf