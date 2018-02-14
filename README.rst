==========
WT_UHF_Hub (Currently Broken)
==========


.. image:: https://img.shields.io/pypi/v/wt_uhf_hub.svg
        :target: https://pypi.python.org/pypi/wt_uhf_hub

.. image:: https://img.shields.io/travis/ZSPina/wt_uhf_hub.svg
        :target: https://travis-ci.org/ZSPina/wt_uhf_hub

.. image:: https://readthedocs.org/projects/wt-uhf-hub/badge/?version=latest
        :target: https://wt-uhf-hub.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




-Installation on Debian
 -------------
 -
 -You can clone the public repository:
 -    
 -.. code-block:: terminal
 -
 -    $ git clone git://github.com/ZSPina/wt_uhf_hub
 -    $ cd wt_uhf_hub
 -    $ python setup.py install
 -        
 -Install a prefix to PyBOMBS for libhackrf.so
 -
 -.. code-block:: terminal
 -
 -    $ pybombs prefix init ~/prefix/default/
 -    $ pybombs install hackrf
 -    
 -Run the wt_uhf_hub program in terminal:
  
 -.. code-block:: terminal
  
 -    $ cd wt_uhf_hub
 -    $ python wt_uhf_hub.py
 -    
  Features
  --------
  
  * TODO
 - * Fill in documentation
 - * Get PyBombs to install hackrf automatically

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
