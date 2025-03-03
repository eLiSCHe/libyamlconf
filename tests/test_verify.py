"""Tests for config verification."""

import logging

from pathlib import Path

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


class TestVerify:
    """Tests for config verification."""

    def test_load_config(self):
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

    def test_additional_config(self, caplog):
        """Unused config parameters shall be logged."""
        config_file = test_data / "not_used.yaml"
        files = [["referenced"]]

        with caplog.at_level(logging.WARNING):
            load_and_verify(config_file, Config, relative_path_keys=files)
            assert "config file contains not used parameters" in caplog.text

    def test_missing_config(self):
        """Missing config parameter shall raise an ValidationError exception."""
        config_file = test_data / "missing.yaml"
        files = [["referenced"]]

        with pytest.raises(ValidationError):
            load_and_verify(config_file, Config, relative_path_keys=files)

    def test_missing_referenced_file(self):
        """Missing referenced file shall raise an InvalidConfiguration exception."""
        config_file = test_data / "invalid.yaml"
        files = [["referenced"]]

        config: Config = load_and_verify(config_file, Config, relative_path_keys=files)

        assert config.referenced == test_data / "other.txt"

        with pytest.raises(InvalidConfiguration):
            verify_files_exist(config, files)

    def test_invalid_file_spec(self, caplog):
        """Not existing file key path shall raise an InvalidConfiguration exception."""
        config_file = test_data / "config.yaml"
        files = [["referenced"], ["wrong", "path"]]

        with caplog.at_level(logging.DEBUG):
            config: Config = load_and_verify(config_file, Config, relative_path_keys=files)
            assert "No match for path ['wrong', 'path'] for layer" in caplog.text

        with pytest.raises(InvalidConfiguration):
            verify_files_exist(config, files)
