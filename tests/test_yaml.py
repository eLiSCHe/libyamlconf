"""Tests for YAML parsing."""

from pathlib import Path

import pytest

from libyamlconf.yaml import (
    _load_yaml,
    InvalidConfiguration,
    YamlLoader,
    _get_paths,
    _path_generator,
)

test_data = Path(__file__).parent / "data" / "yaml"


class TestYaml:
    """Test for YAML parsing."""

    def test_parse_simple_yaml(self) -> None:
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

    def test_yaml_hierarchy(self) -> None:
        """Test inheritance of YAML files."""
        config = test_data / "derived1.yaml"

        loader = YamlLoader()

        data = loader.load(config)

        assert loader._parent_key not in data
        assert data["a"] == 1
        assert data["b"] == 2
        assert data["c"] == 9

    def test_relative_path(self) -> None:
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

    def test_no_config_file(self) -> None:
        """No config file should cause InvalidConfiguration."""
        invalid = test_data / "none.yaml"

        loader = YamlLoader()

        with pytest.raises(InvalidConfiguration):
            loader.load(invalid)

    def test_invalid_root(self) -> None:
        """Invalid root node should cause InvalidConfiguration."""
        invalid = test_data / "invalid_root.yaml"

        loader = YamlLoader()

        with pytest.raises(InvalidConfiguration):
            loader.load(invalid)

    def test_multi_base(self) -> None:
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

    def test_multi_dirs(self) -> None:
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

    def test_single_file(self) -> None:
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

    def test_merge_conflict_object(self) -> None:
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

    def test_get_paths_miss(self) -> None:
        """get_paths shall return [] for a miss."""
        data = {"test": {"hello": "world"}}

        entries = _get_paths(data, ["test", "hello"])
        assert len(entries) == 1
        assert "hello" in entries[0]
        assert entries[0]["hello"] == "world"

        value = _get_paths(data, ["test", "other"])
        assert value == []

    def test_path_generator(self) -> None:
        simple = test_data / "complex.yaml"

        data = _load_yaml(simple)

        path = ["group_a", "child_a_1", "list_a_1", "second"]
        expected_results = [
            {"sub_child_a_1_2": "value_a_1_2_1", "second": "value_a_1_2_2"},
            {"sub_list_child_a_1_3_2": "value_a_1_3_2_1", "second": "value_a_1_3_2_2"},
        ]

        for result, expected_result in zip(_path_generator(data=data, path=path), expected_results):
            assert result == expected_result

        path = ["group_b", "list_b_1", "sub_child_b_1_3", "second"]
        expected_results = [
            {"sub_list_child_b_1_3_2": "value_b_1_3_2_1", "second": "value_b_1_3_2_2"},
        ]

        for result, expected_result in zip(_path_generator(data=data, path=path), expected_results):
            assert result == expected_result

        path = ["group_c", "level1", "level2", "level3", "level4"]
        assert {"level4": "hello"} == next(_path_generator(data, path), None)

        path = ["group_d", "l2", "l2s1", "l2s2"]
        assert {"l2s2": "world"} == next(_path_generator(data, path), None)

    def test_path_generator_modify(self) -> None:
        complex = test_data / "complex.yaml"

        data = _load_yaml(complex)

        path = ["group_a", "child_a_1", "list_a_1", "second"]
        expected_results = [
            {"sub_child_a_1_2": "value_a_1_2_1", "second": "value_a_1_2_2"},
            {"sub_list_child_a_1_3_2": "value_a_1_3_2_1", "second": "value_a_1_3_2_2"},
        ]

        for result, expected_result in zip(_path_generator(data=data, path=path), expected_results):
            assert result == expected_result
            result["second"] = result["second"] + "_modified"

        expected_results = [
            {"sub_child_a_1_2": "value_a_1_2_1", "second": "value_a_1_2_2_modified"},
            {"sub_list_child_a_1_3_2": "value_a_1_3_2_1", "second": "value_a_1_3_2_2_modified"},
        ]

        for result, expected_result in zip(_path_generator(data=data, path=path), expected_results):
            assert result == expected_result

    def test_resolve_complex_paths(self) -> None:
        config_file = test_data / "complex_paths.yaml"

        loader = YamlLoader(relative_path_keys=[["bases", "file"]])
        data = loader.load(config_file)

        assert data["bases"][0]["file"] == config_file.parent / "base1.yaml"
        assert data["bases"][1]["file"] == config_file.parent / "base2.yaml"

    def test_resolve_files(self) -> None:
        """Test for resolving file paths."""
        config_file = test_data / "resolve_paths.yaml"

        loader = YamlLoader(relative_path_keys=[["file"], ["list_with_files", "file"], ["file_list"], ["url"]])
        data = loader.load(config_file)

        assert data["file"] == config_file.parent / "other_include.txt"
        assert data["url"] == "http://www.google.de"
        assert data["list_with_files"][0]["file"] == config_file.parent / "other" / "include.txt"
        assert data["file_list"][0] == config_file.parent / "other" / "include.txt"
        assert data["file_list"][1] == config_file.parent / "other_include.txt"
        assert data["file_list"][2] == "https://www.google.de"
