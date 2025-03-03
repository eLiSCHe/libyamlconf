"""Tests for YAML parsing."""

from pathlib import Path

import pytest

from libyamlconf.yaml import _load_yaml, InvalidConfiguration, YamlLoader, _get_value_for_path, _set_value_for_path

test_data = Path(__file__).parent / "data" / "yaml"


class TestYaml:
    """Test for YAML parsing."""

    def test_parse_simple_yaml(self):
        """Load a simple YAML file."""
        simple = test_data / "simple.yaml"

        data = _load_yaml(simple)

        assert data["hello"] == "world"
        assert len(data["list"]) == 3
        assert data["object"]["other"] == "data"

    def test_invalid_parent_type(self):
        """Invalid parent type shall cause an exception."""
        invalid = test_data / "invalid_base.yaml"

        loader = YamlLoader()

        with pytest.raises(InvalidConfiguration):
            loader.load(invalid)

    def test_yaml_hierarchy(self):
        """Test inheritance of YAML files."""
        config = test_data / "derived1.yaml"

        loader = YamlLoader()

        data = loader.load(config)

        assert loader._parent_key not in data
        assert data["a"] == 1
        assert data["b"] == 2
        assert data["c"] == 9

    def test_relative_path(self):
        """Test completion of relative paths."""
        config = test_data / "derived1.yaml"

        loader = YamlLoader(relative_path_keys=[["file"], ["obj", "file"]])

        data = loader.load(config)

        assert "file" in data
        file = Path(__file__).parent / "data" / "yaml" / "other_include.txt"
        assert data["file"] == file

        assert "obj" in data
        assert "file" in data["obj"]
        file = Path(__file__).parent / "data" / "yaml" / "other" / "include.txt"
        assert data["obj"]["file"] == file

    def test_no_config_file(self):
        """No config file should cause InvalidConfiguration."""
        invalid = test_data / "none.yaml"

        loader = YamlLoader()

        with pytest.raises(InvalidConfiguration):
            loader.load(invalid)

    def test_invalid_root(self):
        """Invalid root node should cause InvalidConfiguration."""
        invalid = test_data / "invalid_root.yaml"

        loader = YamlLoader()

        with pytest.raises(InvalidConfiguration):
            loader.load(invalid)

    def test_multi_base(self):
        """Test inheritance of multiple YAML files."""
        config = test_data / "derived2.yaml"

        loader = YamlLoader(relative_path_keys=[["file"]])

        data = loader.load(config)

        assert loader._parent_key not in data
        assert data["a"] == 1
        assert data["b"] == 2
        assert data["c"] == 9
        file = Path(__file__).parent / "data" / "yaml" / "other_include.txt"
        assert data["file"] == file
        assert "obj" in data
        assert data["obj"]["some"] == "other"
        assert data["obj"]["hello"] == "world"
        assert "list" in data
        assert data["list"][0] == "a"
        assert data["list"][1] == "b"
        assert data["list"][2] == "c"

    def test_multi_dirs(self):
        """Test inheritance of multiple YAML files from multiple dirs."""
        config = test_data / "derived3.yaml"

        loader = YamlLoader(relative_path_keys=[["file"]])

        data = loader.load(config)

        assert loader._parent_key not in data
        assert data["a"] == 1
        assert data["b"] == 2
        assert data["c"] == 10
        assert data["d"] == 5
        file = Path(__file__).parent / "data" / "yaml" / "other" / "include.txt"
        assert data["file"] == file

    def test_single_file(self):
        """Test loading of config without inheritance."""
        config = test_data / "base1.yaml"

        loader = YamlLoader(relative_path_keys=[["file"]])

        data = loader.load(config)

        assert loader._parent_key not in data
        assert data["a"] == 1
        assert data["b"] == 2
        assert data["c"] == 3
        file = Path(__file__).parent / "data" / "yaml" / "other_include.txt"
        assert data["file"] == file

    def test_merge_conflict_object(self):
        """Merge conflict shall cause InvalidConfiguration."""
        config = test_data / "conflict1.yaml"

        loader = YamlLoader(relative_path_keys=[["file"]])

        with pytest.raises(InvalidConfiguration):
            loader.load(config)

    def test_merge_conflict_list(self):
        """Merge conflict shall cause InvalidConfiguration."""
        config = test_data / "conflict2.yaml"

        loader = YamlLoader(relative_path_keys=[["file"]])

        with pytest.raises(InvalidConfiguration):
            loader.load(config)

    def test_get_value_for_path_miss(self):
        """get_value_for_path shall return None for a miss."""
        data = { "test": { "hello": "world" } }
        
        value = _get_value_for_path(data, ["test", "hello"])
        assert value == "world"
        
        value = _get_value_for_path(data, ["test", "other"])
        assert value is None

    def test_set_value_for_path_miss(self):
        """get_value_for_path shall return None for a miss."""
        data = { "a": { "b": { "c": "d" } } }
        
        result = _set_value_for_path(data, ["a", "b", "c"], "d")
        assert result
        
        result = _set_value_for_path(data, ["a", "b", "d"], "value")
        assert not result
        
        result = _set_value_for_path(data, ["a", "e", "c"], "value")
        assert not result
