Welcome to the `sphinxcontrib-packages` documentation
=====================================================

This `sphinx <http://sphinx.pocoo.org/>`__ extension provides some directives to
see what tools are available on the compiling machine. I wrote this because I was developping a sphinx extension calling system commands, and I wanted to be able to use is on `readthedocs <http://readthedocs.org>`__, but I did not know which tools were available there: the `official list of installed tools <https://docs.readthedocs.org/en/latest/builds.html#packages-installed-in-the-build-environment>`__ is pretty scarce…

.. warning::

    If your are reading this on `readthedocs <http://readthedocs.org>`__, keep in mind that thoses lists are not official. It is not guaranteed that those tools will remain available in the future: they only reflects what was available when this documentation was compiled.

    I do not know and I have nothing to do with `readthedocs <http://readthedocs.org>`__, so I do not know how they choose what to install.

Installed tools
---------------

If you want to see installed tools, the list is here. Else, se below for more information about this package.

.. toctree::

   platform
   pyversions
   python
   bin
   c
   deb
   latex


Download and install
--------------------

See the `main project page <http://git.framasoft.org/spalax/sphinxcontrib-packages>`_ for
instructions, and `changelog
<https://git.framasoft.org/spalax/sphinxcontrib-packages/blob/master/CHANGELOG>`_.

Usage
-----

Add ``sphinxcontrib.packages`` to the list of sphinx extensions in your config files, and use of the directives provided by this package.
