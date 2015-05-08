Installed python packages
=========================

This information is provided by the directive::

  .. packages:python::
     :bin: BINARY

It lists available python packgaes, using ``BINARY`` as the python binary.
Note that packages only available in a `virtualenv` may appear, and system
packages may not be displayed if run in a `virtualenv`.

* To list installed python2 packages::

    .. packages:python::
       :bin: python2

* To list installed python3 packages::

    .. packages:python::
       :bin: python3

.. toctree::

    python/python2
    python/python3
