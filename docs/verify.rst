Verify module
=============

.. toctree::
   :maxdepth: 2
   :caption: Contents:

.. automodule:: libyamlconf.verify

The primary API for loading and verifying a configuration is load_and_verify:

.. autofunction:: libyamlconf.verify.load_and_verify

To verify that all referenced files exist, the function verify_files_exist can be used.

.. autofunction:: libyamlconf.verify.verify_files_exist
