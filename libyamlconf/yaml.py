"""Load and merge YAMl configuration."""

import os
import logging

from pathlib import Path
from typing import Any

import yaml


class InvalidConfiguration(Exception):
    """Raised if a severe configuration issue is found."""


def _invalid_config(message: str) -> None:
    """Raise an InvalidConfiguration exception."""
    logging.critical(message)
    raise InvalidConfiguration(message)


def _load_yaml(file: Path) -> dict[str, Any]:
    """Load the content of a single YAML file."""
    if not os.path.isfile(file):
        _invalid_config(f"Config file {file} does not exist!")

    with open(file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _contains_path(data: dict, path: list[str]) -> bool:
    """Get the config value for the given keys path."""
    for key in path:
        if key in data:
            data = data[key]
        else:
            return False
    return True


def _get_value_for_path(data: dict, path: list[str]) -> Any | None:
    """Get the config value for the given keys path."""
    for key in path:
        if key in data:
            data = data[key]
        else:
            return None
    return data


def _set_value_for_path(data: dict, path: list[str], value: Any) -> bool:
    """Set the config value for the given keys path."""
    for key in path[:-1]:
        if key in data:
            data = data[key]
        else:
            return False
    data[path[-1]] = value
    return True


def _merge_values(current: Any, new: Any) -> Any:
    """Merge two values where the key appears multiple times."""
    if isinstance(current, str) or isinstance(current, int) or isinstance(current, float) or isinstance(current, Path):
        # Overwrite old value for simple types.
        return new
    elif isinstance(current, dict):
        if isinstance(new, dict):
            # Merge dicts, new entry wins.
            for key in new.keys():
                current[key] = new[key]
            return current
        else:
            _invalid_config(f"Unsupported types for merge: {current} ({type(current)}), {new} ({type(new)})")

    elif isinstance(current, list):
        if isinstance(new, list):
            current.extend(new)
            return current
        else:
            _invalid_config(f"Unsupported types for merge: {current} ({type(current)}), {new} ({type(new)})")

    else:  # pragma: no cover
        _invalid_config(f"Unsupported types for merge: {current} ({type(current)}), {new} ({type(new)})")


class YamlLoader:
    def __init__(self, parent_key: str = "base", relative_path_keys: list[str] = []):
        self._parent_key: str = parent_key
        self._relative_path_keys: list[list[str]] = relative_path_keys
        self._layers: list[Path] = []
        self._layer_data: dict[Path, dict] = {}
        self._data: dict[str, Any] = {}

    def _reset(self):
        """Reset parsing data structures."""
        self._layers: list[Path] = []
        self._layer_data: dict[Path, dict] = {}
        self._data: dict[str, Any] = {}

    def _recursive_load(self, file: Path) -> dict[str, Any]:
        """Recursive load the YAML hierarchy."""
        if file in self._layers:
            logging.warning(
                "Config file %s is inherited multiple times. It was already loaded and will be skipped now.", file
            )
            return

        self._layers.append(file)
        data = _load_yaml(file)
        logging.debug("Config data from %s: %s", file, data)

        if not isinstance(data, dict):
            _invalid_config(f"Unsupported root node type: {data} ({type(data)})")

        self._layer_data[file] = data

        if self._parent_key in data:
            if isinstance(data[self._parent_key], str):
                next_file = file.parent / Path(data[self._parent_key])
                logging.debug("%s has single parent file %s", file, next_file)
                self._recursive_load(next_file)

            elif isinstance(data[self._parent_key], list):
                logging.debug("%s has multiple parent files: %s", file, data[self._parent_key])

                for parent_file in data[self._parent_key]:
                    next_file = file.parent / parent_file
                    logging.debug("Loading parent file %s of %s", next_file, file)
                    self._recursive_load(next_file)

            else:
                _invalid_config(
                    f"Unsupported value for {self._parent_key}: {data[self._parent_key]} ({type(data[self._parent_key])})"
                )

    def _resolve_relative_paths(self):
        """Convert relative paths to absolute paths."""
        for layer in self._layers:
            for path in self._relative_path_keys:
                if _contains_path(self._layer_data[layer], path):
                    file = _get_value_for_path(self._layer_data[layer], path)
                    resolved = layer.parent / file
                    logging.debug("Resolving path %s to %s for config file %s.", file, resolved, layer)
                    _set_value_for_path(self._layer_data[layer], path, resolved)
                else:
                    logging.debug("No match for path %s for layer %s.", path, layer)

    def _merge_config_data(self):
        """Merge the config layers."""
        # Init data using lowest layer
        self._data = self._layer_data[self._layers[-1]]

        if self._parent_key in self._data:
            del self._data[self._parent_key]

        logging.debug("Initial data from layer %s: %s", self._layers[-1], self._data)

        if len(self._layers) <= 1:
            logging.debug("No further layers: %s", self._layers)
            return

        layers = self._layers.copy()
        layers.reverse()
        # Skip lowest layer
        layers = layers[1:]

        logging.debug("Merging layers: %s", layers)

        for layer in layers:
            data = self._layer_data[layer]
            for key, value in data.items():
                if key == self._parent_key:
                    # Do not merge parent key.
                    continue

                if key not in self._data:
                    logging.debug("Using key %s with value %s from file %s.", key, value, layer)
                    self._data[key] = value
                else:
                    merged = _merge_values(self._data[key], data[key])
                    logging.debug(
                        "Merging values %s and %s for key %s from file %s. Result: %s",
                        self._data[key],
                        data[key],
                        key,
                        layer,
                        merged,
                    )
                    self._data[key] = merged

    def load(self, file: Path) -> dict[str, Any]:
        """Load a hierarchical YAML file."""
        self._reset()

        self._recursive_load(file)

        logging.info("Config file layers:\n%s", "\n".join([str(layer) for layer in self._layers]))

        self._resolve_relative_paths()

        self._merge_config_data()

        logging.info("Resulting configuration:\n%s", self._data)

        return self._data
