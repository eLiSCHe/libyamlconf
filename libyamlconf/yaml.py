"""
Load and merge YAMl configuration.

This module implements the hierarchical YAML parsing.
"""

import os
import logging

from pathlib import Path
from typing import Any

import yaml


class InvalidConfiguration(Exception):
    """Raised if a severe configuration issue is found."""


def _invalid_config(message: str) -> None:
    """
    Raise an InvalidConfiguration exception.

    This function raises and InvalidConfiguration exception using the given message.
    It also logs the message as critical error.

    :param message: Error message for the log and the exception.

    :raises InvalidConfiguration: InvalidConfiguration is used to signal and invalid yaml configuration.
    """
    logging.critical(message)
    raise InvalidConfiguration(message)


def _load_yaml(file: Path) -> dict[str, Any]:
    """
    Load the content of a single YAML file.

    This function raises an InvalidConfiguration exception if the file does not exist.

    :param file: Path of the YAMl config file to parse.
    :return: Data contained in the YAML config file.
    """
    if not os.path.isfile(file):
        _invalid_config(f"Config file {file} does not exist!")

    with open(file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _path_generator(data: dict, path: list[str]) -> Any:
    """
    Create an generator for the given path and the given data.

    This generator yields the matching paths.

    :param data: Data to get the specified value.
    :param path: Keys path.
    :return: Path generator yielding the path matches.
    """
    if isinstance(data, list):
        for entry in data:
            if isinstance(entry, dict):  # pragma: no branch
                if path[0] in entry and len(path) == 1:
                    yield entry
                elif path[0] in entry:
                    for match in _path_generator(entry, path[1:]):
                        yield match

    elif isinstance(data, dict):  # pragma: no branch
        if len(path) == 1 and path[0] in data:
            yield data
        elif path[0] in data:
            for match in _path_generator(data[path[0]], path[1:]):
                yield match


def _contains_path(data: dict, path: list[str]) -> bool:
    """
    Test if a given key path exists in the config data.

    This function tries to walk along the given keys path through the given data
    and returns true if the path exists, and false otherwise.

    >>> data = { "test": { "hello": "world" } }
    >>> _contains_path(data, ["test", "hello"])
    True

    :param data: Data to check for the keys path.
    :param path: Keys path.
    :return: True if the path exists, false else.
    """
    generator = _path_generator(data, path)
    return next(generator, None) is not None


def _get_paths(data: dict, path: list[str]) -> list[Any]:
    """
    Get the config value for the given keys path.

    This functions walks along the given key path through the given data
    and returns the value specified by this path, if it exists.

    >>> data = { "test": { "hello": "world" } }
    >>> entries = _get_paths(data, ["test", "hello"])
    >>> assert len(entries) == 1
    >>> entry = entries[0]
    >>> assert "hello" in entry
    >>> entry["hello"]
    'world'

    :param data: Data to get the specified value.
    :param path: Keys path.
    :return: Value specified by the keys path or None.
    """
    generator = _path_generator(data, path)
    return [match for match in generator]


def _merge_values(current: Any, new: Any) -> Any:
    """
    Merge two values where the key appears multiple times.

    This function implements the config data merge, which is needed if multiple YAML config files
    in the hierarchy provide the same config key path. The general strategy is that the higher value
    in the config files hierarchy wins. Lists are in general concatenated and dicts are merged by adding
    new values and overwriting existing values.

    :param current: Current value of the config key.
    :param new: New value of the config key from the higher config file.
    :returns: Merged config value.
    """
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
    def __init__(self, parent_key: str = "base", relative_path_keys: list[list[str]] = []):
        """
        Create a new YamlLoader instance.

        :param parent_key: Key used to reference included config files.
        :param relative_path_keys: List of list of config keys. Each list is interpreted as one config path,
                                   and the value of each path is completed to an absolute file path with respect
                                   to the config file location.
        """
        self._parent_key: str = parent_key
        self._relative_path_keys: list[list[str]] = relative_path_keys
        self._layers: list[Path] = []
        self._layer_data: dict[Path, dict] = {}
        self._data: dict[str, Any] = {}

    def _reset(self) -> None:
        """Reset parsing data structures."""
        self._layers = []
        self._layer_data = {}
        self._data = {}

    def _recursive_load(self, file: Path) -> None:
        """
        Recursive load the YAML hierarchy.

        :param file: File path of the next YAML config file to load and add.
        """
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

    def _resolve_relative_paths(self) -> None:
        """Convert relative paths to absolute paths."""
        for layer in self._layers:
            for path in self._relative_path_keys:
                if _contains_path(self._layer_data[layer], path):
                    entries = _get_paths(self._layer_data[layer], path)
                    for entry in entries:
                        value = entry[path[-1]]
                        if isinstance(value, str):
                            file = value
                            resolved = layer.parent / file
                            logging.debug("Resolving path %s to %s for config file %s.", file, resolved, layer)
                            entry[path[-1]] = resolved
                        elif isinstance(value, list):
                            resolved_files = []
                            for file in value:
                                resolved = layer.parent / file
                                logging.debug("Resolving path %s to %s for config file %s.", file, resolved, layer)
                                resolved_files.append(resolved)
                            # Replace the list content
                            entry[path[-1]] = resolved_files
                        else:  # pragma: no cover
                            # Should never happen
                            raise Exception(f"Unexpected match {entry} for path {path}!")

                else:
                    logging.debug("No match for path %s for layer %s.", path, layer)

    def _merge_config_data(self) -> None:
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
        """
        Load a hierarchical YAML file.

        :param file: Path of the YAML config file to load.
        :return: Merged configuration values for the YAML config file hierarchy.
        """
        self._reset()

        self._recursive_load(file)

        logging.info("Config file layers:\n%s", "\n".join([str(layer) for layer in self._layers]))

        self._resolve_relative_paths()

        self._merge_config_data()

        logging.info("Resulting configuration:\n%s", self._data)

        return self._data
