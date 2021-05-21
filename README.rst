`sphinxcontrib-packages` 📦 Display a list of tools available on the host machine
=================================================================================

This `sphinx <http://sphinx.pocoo.org/>`__ extension provides some directives
to see what tools are available on the compiling machine. I wrote this because
I was developing a sphinx extension calling system commands, and I wanted to
be able to use is on `readthedocs <http://readthedocs.io>`__, but I did not
know which tools were available there
(and the `Dockerfile <https://hub.docker.com/r/readthedocs/build/~/dockerfile>`__ is not precise enough).

What's new?
-----------

See `changelog <https://git.framasoft.org/spalax/sphinxcontrib-packages/blob/main/CHANGELOG.md>`_.

Install
-------

This module is compatible with python 3 only.

See the end of list for a (quick and dirty) Debian package.

* From sources:

  * Download: https://pypi.python.org/pypi/sphinxcontrib-packages
  * Install (in a `virtualenv`, if you do not want to mess with your distribution installation system)::

      python setup.py install

* From pip::

    pip install sphinxcontrib-packages

* Quick and dirty Debian (and Ubuntu?) package

  This requires `stdeb <https://github.com/astraw/stdeb>`_ to be installed::

      python setup.py --command-packages=stdeb.command bdist_deb
      sudo dpkg -i deb_dist/python3-sphinxcontrib-packages-<VERSION>_all.deb

Documentation
-------------

The documentation is available on `readthedocs <http://packages.readthedocs.io>`_.  You can build it using::

  cd doc && make html
