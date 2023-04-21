Welcome to the `sphinxcontrib-packages` documentation
=====================================================

This `sphinx <http://sphinx.pocoo.org/>`__ extension provides some directives to
see what tools are available on the compiling machine. I wrote this because I was developing a sphinx extension calling system commands, and I wanted to be able to use is on `readthedocs <http://readthedocs.io>`__, but I did not know which tools were available there
(and the `Dockerfile <https://hub.docker.com/r/readthedocs/build/~/dockerfile>`__ is not precise enough).

.. warning::

    If your are reading this on `readthedocs <http://readthedocs.io>`__, keep in mind that those lists are not official. It is not guaranteed that those tools will remain available in the future: they only reflects what was available when this documentation was compiled.

    I do not know and I have nothing to do with the `readthedocs <http://readthedocs.io>`__ team, so I do not know how they choose what to install.

.. warning::

   This package was written before `readthedocs <http://readthedocs.io>`__ started `using Docker <https://docs.readthedocs.io/en/stable/config-file/v2.html>`__. Since you can run commands before compilation and install Debian packages, I am not sure how relevant this package is now.

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
<https://git.framasoft.org/spalax/sphinxcontrib-packages/blob/main/CHANGELOG.md>`_.

Usage
-----

Add ``sphinxcontrib.packages`` to the list of sphinx extensions in your config files, and use of the directives provided by this package.
