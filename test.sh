#!/bin/bash

clear

echo "=================== Linters ===================="

echo "------------------- Ruff -----------------------"

uv run ruff check --output-format=github .

echo "------------------- darglint--------------------"

uv run darglint --verbosity 2 --docstring-style sphinx libyamlconf

echo "=================== Tests ===================="

uv run coverage run -m pytest -v -s
uv run coverage report -m
uv run coverage html
