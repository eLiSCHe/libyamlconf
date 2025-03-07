YAML module
===========

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. automodule:: libyamlconf.yaml

Classes
-------

The main functionality is provided by the YamlLoader class:

.. autoclass:: libyamlconf.yaml::YamlLoader
    :members:

In case of severe configuration issues, the InvalidConfiguration exception is raised:

.. autoclass:: libyamlconf.yaml::InvalidConfiguration
    :members:

Functions
---------

The YamlLoader makes use of a bunch of helper functions.

On of the core features, the merging of duplicate keys, is implemented as _merge_values:

.. autofunction:: libyamlconf.yaml._merge_values

To ease the handling of dicts, a bunch of helper methods are available:

.. autofunction:: libyamlconf.yaml._path_generator

.. autofunction:: libyamlconf.yaml._contains_path

.. autofunction:: libyamlconf.yaml._get_paths

To also log the issue in case of an exception, _invalid_config is used:

.. autofunction:: libyamlconf.yaml._invalid_config

To load the content of a YAML file, the pyyaml module is used and called in _load_yaml:

.. autofunction:: libyamlconf.yaml._load_yaml

The function _is_url is used to skip URLs when resolving relative paths or checking
that the files exist:

.. autofunction:: libyamlconf.yaml._is_url
