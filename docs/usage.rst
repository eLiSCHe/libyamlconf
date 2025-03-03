Usage
=====

Libyamlconf makes use of `Pydantic <https://docs.pydantic.dev/latest/>`_
for specifying the configuration format. A simple config format specification
can look like:

.. highlight:: python
.. code-block:: python

    from pathlib import Path
    from pydantic import BaseModel

    class Config(BaseModel):
        number: int
        pi: float
        hello: str
        some: str
        referenced: Path

The corresponding configuration YAMl looks like:

.. highlight:: yaml
.. code-block:: yaml

    number: 1
    pi: 3.14
    hello: world
    some: value
    referenced: referenced.file


The primary interface of libyamlconf to load such a configuration is `load_and_verify`.

.. highlight:: python
.. code-block:: python

    from libyamlconf.verify import load_and_verify
    
    config: Config = load_and_verify("config.yaml", Config, relative_path_keys=[["referenced"]])

If needed, the function `verify_files_exist` can be used to ensure the referenced files exist on the local machine:

.. highlight:: python
.. code-block:: python

    from libyamlconf.verify import verify_files_exist
    
    verify_files_exist(config, [["referenced"]])

This function will raise an InvalidConfiguration if one of the referenced files is missing.

Not used YAML configuration values are ignored, but reported as warning logs.
