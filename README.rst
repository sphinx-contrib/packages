Description of the `sphinxcontrib-packages` Sphinx Extension
============================================================

|sources| |pypi| |documentation| |license|

This `sphinx <http://sphinx.pocoo.org/>`__ extension provides some directives
to see what tools are available on the compiling machine. I wrote this because
I was developping a sphinx extension calling system commands, and I wanted to
be able to use is on `readthedocs <http://readthedocs.org>`__, but I did not
know which tools were available there: the `official list of installed tools
<https://docs.readthedocs.org/en/latest/builds.html#packages-installed-in-the-build-environment>`__
is pretty scarce…

What's new?
-----------

See `changelog
<https://git.framasoft.org/spalax/sphinxcontrib-packages/blob/master/CHANGELOG>`_.

Install
-------

This module is compatible with both python 2 and 3.

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

The documentation is available on `readthedocs
<http://packages.readthedocs.org>`_.  You can build it using::

  cd doc && make html

.. |documentation| image:: http://readthedocs.org/projects/packages/badge
  :target: http://packages.readthedocs.org
.. |pypi| image:: https://img.shields.io/pypi/v/sphinxcontrib-packages.svg
  :target: http://pypi.python.org/pypi/sphinxcontrib-packages
.. |license| image:: https://img.shields.io/pypi/l/sphinxcontrib-packages.svg
  :target: http://www.gnu.org/licenses/agpl-3.0.html
.. |sources| image:: https://img.shields.io/badge/sources-sphinxcontrib--packages-brightgreen.svg
  :target: http://git.framasoft.org/spalax/sphinxcontrib-packages
