import sys
from pathlib import Path

from sphinx_pyproject import SphinxConfig
from libyamlconf import __version__ as libyamlconf_version

sys.path.insert(0, str(Path('..').resolve()))

config = SphinxConfig("../pyproject.toml", globalns=globals(), config_overrides={"version": libyamlconf_version})

# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'eLiSCHe: libyamlconf'
copyright = "2025, Thomas Irgang"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
