# libyamlconf

Libyamlconf supports loading configuration form hierarchical YAML files.

For more details see docs/index.rst or https://elische.github.io/libyamlconf/.

## Example

The folder `example` contains an example app using libyamlconf.

Try the example:

- Setup [uv](https://github.com/astral-sh/uv)
- Run the example: `uv run python example/main.py`

## Contribute

This library makes use of [uv](https://github.com/astral-sh/uv) and [ruff](https://github.com/astral-sh/ruff).

Use the following steps to prepare your development environment:

- Prepare a virtual environment and install development dependencies: `uv sync`
- Activate the virtual environment: `source .venv/bin/activate`

Please test your changes locally before raising and PR using `./test.sh`
