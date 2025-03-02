"""Tests for YAML parsing."""

from pathlib import Path

from libyamlconf.yaml import load_yaml

test_data = Path(__file__).parent / "data" / "yaml"


class TestYaml:
    """Test for YAML parsing."""

    def test_parse_simple_yaml(self):
        """Load a simple YAML file."""
        simple = test_data / "simple.yaml"

        data = load_yaml(simple)

        assert data["hello"] == "world"
        assert len(data["list"]) == 3
        assert data["object"]["other"] == "data"
