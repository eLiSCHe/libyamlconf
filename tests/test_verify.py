"""Tests for config verification."""

import logging

from pathlib import Path
from typing import Any

import pytest

from pydantic import BaseModel, ValidationError

from libyamlconf.yaml import InvalidConfiguration
from libyamlconf.verify import load_and_verify, verify_files_exist

LOGGER = logging.getLogger(__name__)
test_data = Path(__file__).parent / "data" / "verify"


class Config(BaseModel):
    number: int
    pi: float
    hello: str
    some: str
    referenced: Path


class ListWithFiles(BaseModel):
    name: str
    file: Path


class ResolvePaths(BaseModel):
    file: Path
    url: Path | str
    list_with_files: list[ListWithFiles]
    file_list: list[Path | str]


class InvalidFileList(BaseModel):
    files: list[Path | str]


class TestVerify:
    """Tests for config verification."""

    def test_load_config(self) -> None:
        """Load and verify a valid configuration."""
        config_file = test_data / "config.yaml"
        files = [["referenced"]]

        config: Config = load_and_verify(config_file, Config, relative_path_keys=files)

        assert config.number == 1
        assert config.pi == 3.14
        assert config.hello == "world"
        assert config.some == "other"
        assert config.referenced == test_data / "referenced.file"

        verify_files_exist(config, files)

    def test_additional_config(self, caplog) -> None:
        """Unused config parameters shall be logged."""
        config_file = test_data / "not_used.yaml"
        files = [["referenced"]]

        with caplog.at_level(logging.WARNING):
            load_and_verify(config_file, Config, relative_path_keys=files)
            assert "config file contains not used parameters" in caplog.text

    def test_missing_config(self) -> None:
        """Missing config parameter shall raise an ValidationError exception."""
        config_file = test_data / "missing.yaml"
        files = [["referenced"]]

        with pytest.raises(ValidationError):
            load_and_verify(config_file, Config, relative_path_keys=files)

    def test_missing_referenced_file(self) -> None:
        """Missing referenced file shall raise an InvalidConfiguration exception."""
        config_file = test_data / "invalid.yaml"
        files = [["referenced"]]

        config: Config = load_and_verify(config_file, Config, relative_path_keys=files)

        assert config.referenced == test_data / "other.txt"

        with pytest.raises(InvalidConfiguration):
            verify_files_exist(config, files)

    def test_invalid_file_spec(self, caplog) -> None:
        """Not existing file key path shall raise an InvalidConfiguration exception."""
        config_file = test_data / "config.yaml"
        files = [["referenced"], ["wrong", "path"]]

        with caplog.at_level(logging.DEBUG):
            config: Config = load_and_verify(config_file, Config, relative_path_keys=files)
            assert "No match for path ['wrong', 'path'] for layer" in caplog.text

        with pytest.raises(InvalidConfiguration):
            verify_files_exist(config, files)

    def test_resolve_url(self) -> None:
        """Test for resolving file paths."""
        config_file = test_data.parent / "yaml" / "resolve_paths.yaml"
        paths = [["file"], ["list_with_files", "file"], ["file_list"], ["url"]]

        config: ResolvePaths = load_and_verify(
            config_file,
            ResolvePaths,
            relative_path_keys=paths,
        )

        assert config.file == config_file.parent / "other_include.txt"
        assert config.url == "http://www.google.de"
        assert config.list_with_files[0].file == config_file.parent / "other" / "include.txt"
        assert config.file_list[0] == config_file.parent / "other" / "include.txt"
        assert config.file_list[1] == config_file.parent / "other_include.txt"
        assert config.file_list[2] == "https://www.google.de"

        verify_files_exist(model=config, relative_path_keys=paths)

    def test_invalid_file_list(self) -> None:
        """Test for resolving file paths."""
        config_file = test_data / "invalid_file_list.yaml"
        paths = [["files"]]

        config: InvalidFileList = load_and_verify(
            config_file,
            InvalidFileList,
            relative_path_keys=paths,
        )

        assert config.files[0] == test_data / "base.yaml"
        assert config.files[1] == test_data / "config.yaml"
        assert config.files[2] == "http://www.google.de"
        assert config.files[3] == test_data / "invalid.txt"

        with pytest.raises(InvalidConfiguration):
            verify_files_exist(model=config, relative_path_keys=paths)
