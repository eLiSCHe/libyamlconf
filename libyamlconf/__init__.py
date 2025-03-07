"""
Libyamlconf provides support parsing and verification of hierarchical YAML files.

For multiple configuration variants, duplicating the whole configuration is bad,
since it comes with a huge maintenance burden.  Libyamlconf makes these cases easy
by allowing deriving configurations. Let's make this more clear using an example.

Assume you want to define the packages installed in a Linux root filesystem as
a YAML fil. This could be a `root.yaml` and look like:

.. highlight:: yaml
.. code-block:: yaml

    packages:
      - systemd
      - udev

Let's further assume that you also want a debug variant providing additional packages.
This could be a `root_debug.yaml` and look like:

.. highlight:: yaml
.. code-block:: yaml

    packages:
      - systemd
      - udev
      - gdbserver

Now, if you want to add a new package to the root filesystem, you have to add it to two files.

Libyamlconf allows to ease this by deriving the `root_debug.yaml` from the `root.yaml`.

.. highlight:: yaml
.. code-block:: yaml

    base: root.yaml
    packages:
      - gdbserver

The `base` key is the default, and can be changed when the YamlLoader is instantiated.

Libyamlconf also allows multiple inheritance, which helps to better structure the configuration.
Let's assume you also want to specify the used APT repositories. Our `repo.yaml` could look like:

.. highlight:: yaml
.. code-block:: yaml

    apt_repos:
      - apt_repo: http://archive.ubuntu.com/ubuntu
        distro: jammy
        components:
        - main
        - universe

This configuration may one the one hand become complex, and on the other hand you may wand to
switch between distributions. You can solve this by extending the inheritance hierarchy.
We can include this repository configuration into `root.yaml`, which also makes it available
for the `root_debug.yaml`.

.. highlight:: yaml
.. code-block:: yaml

    base: repo.yaml
    packages:
      - systemd
      - udev

The resulting `root_debug.yaml` will look like:


.. highlight:: yaml
.. code-block:: yaml

    apt_repos:
      - apt_repo: http://archive.ubuntu.com/ubuntu
        distro: jammy
        components:
        - main
        - universe
    packages:
      - systemd
      - udev
      - gdbserver

Libyamlconf also support multiple inheritance.
You could define a `debug.yaml`, specifying all your debug tools:

.. highlight:: yaml
.. code-block:: yaml

    packages:
      - gdbserver

And then additionally include this file in your `root_debug.yaml`:

.. highlight:: yaml
.. code-block:: yaml

    base:
      - root.yaml
      - debug.yaml

Which would then also result in:

.. highlight:: yaml
.. code-block:: yaml

    apt_repos:
      - apt_repo: http://archive.ubuntu.com/ubuntu
        distro: jammy
        components:
        - main
        - universe
    packages:
      - systemd
      - udev
      - gdbserver
"""

__version__ = "1.2.0"
