"""
Verify the loaded configuration data.
"""

import logging

from pathlib import Path
from typing import Type, Any

from pydantic import BaseModel
from deepdiff import DeepDiff

from libyamlconf.yaml import YamlLoader, _contains_path, _get_value_for_path, _invalid_config


def load_and_verify(
    file: Path, model: Type[BaseModel], parent_key: str = "base", relative_path_keys: list[list[str]] = []
) -> Any:
    """
    Load a config file and verify that it matches a given model.

    :param file: Path of the YAML config file to load.
    :param model: Pydantic model for the loaded data.
    :param parent_key: Key used to reference included config files. Default: "base".
    :param relative_path_keys: List of list of config keys. Each list is interpreted as one config path,
        and the value of each path is completed to an absolute file path with respect
        to the config file location. Default: [].
    :return: Instance of the pydantic model.
    """
    loader = YamlLoader(parent_key=parent_key, relative_path_keys=relative_path_keys)
    # Load YAML data
    data = loader.load(file)
    # User Pydantic model to verify data
    model = model(**data)

    logging.debug("Loaded model: %s (%s)", model, type(model))

    # Check for not used parameters
    model_data = model.model_dump()
    if model_data != data:
        logging.warning(
            "The config file contains not used parameters! Difference to loaded model:\n%s", DeepDiff(data, model_data)
        )

    return model


def verify_files_exist(model: Type[BaseModel], relative_path_keys: list[list[str]]) -> None:
    """
    Verify that the files referenced by relative_path_keys exist.
    :param model: Pydantic model containing the loaded data.
    :param relative_path_keys: List of list of config keys. Each list is interpreted as one config path,
    and the value of each path needs ot be a Path and the pointed file or directory needs to exist.
    """
    data = model.model_dump()
    for path in relative_path_keys:
        if not _contains_path(data, path):
            _invalid_config(f"The path {path} is not contained in the model {model}!")

        file = Path(_get_value_for_path(data, path))
        if not file.exists():
            _invalid_config(f"The file {file} referenced by {path} does not exist!")
