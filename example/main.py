"""
Demo for using libyamlconf.
"""

from pathlib import Path

from pydantic import BaseModel

from libyamlconf.verify import load_and_verify, verify_files_exist
from libyamlconf.yaml import InvalidConfiguration


class Common(BaseModel):
    """
    Configuration subclass.
    """

    base: str
    file: Path


class Config(BaseModel):
    """
    Configuration model for the demo.
    """

    version: int
    common: Common
    some: str
    file: Path


def main() -> None:
    """
    Example for loading and verifying a YAML configuration.
    """
    files = [["common", "file"], ["file"], ["list-with-files", "file"], ["file-list"]]
    config_file = Path(__file__).parent / "config.yaml"

    print("Loading config file...")
    config: Config = load_and_verify(config_file, Config, relative_path_keys=files)
    print(f"Loaded configuration:\n{config}")

    print("Verifying files...")
    try:
        verify_files_exist(config, files)
    except InvalidConfiguration as ex:
        print("The referenced but not existing file 'not-existing.file' is causing an InvalidConfiguration exception:")
        raise ex


if __name__ == "__main__":
    main()
