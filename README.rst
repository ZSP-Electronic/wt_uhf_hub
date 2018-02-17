==========
WT_UHF_Hub
==========


.. image:: https://img.shields.io/pypi/v/wt_uhf_hub.svg
        :target: https://pypi.python.org/pypi/wt_uhf_hub

.. image:: https://img.shields.io/travis/ZSPina/wt_uhf_hub.svg
        :target: https://travis-ci.org/ZSPina/wt_uhf_hub

.. image:: https://readthedocs.org/projects/wt-uhf-hub/badge/?version=latest
        :target: https://wt-uhf-hub.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Installation on fresh Debian image
-------------

1. Expand file system:

.. code-block:: terminal

    $ cd /opt/scripts/tools/
    $ git pull || true
    $ sudo ./grow_partition.sh
    $ sudo reboot
    
2. Upgrade kernal to 4.14:

.. code-block:: terminal

    $ sudo apt-get update
    $ cd /opt/scripts/tools/
    $ git pull
    $ sudo ./update_kernel.sh --bone-kernel --lts-4_14

3. Clone the public repository to directory:

.. code-block:: terminal

    $ git clone git://github.com/ZSPina/wt_uhf_hub
    $ cd wt_uhf_hub
    $ sudo python setup.py install
    $ sudo python installRequired.py
        
4. Install a prefix to PyBOMBS for libhackrf.so:

.. code-block:: terminal

    $ cd
    $ pybombs auto-config
    $ pybombs recipes add-defaults
    $ pybombs prefix init ~/prefix -a myprefix -R gnuradio-default
    $ pybombs install hackrf
    
4.2 Check that libhackrf.so is in the correct file path

.. code-block:: terminal

    $ cd prefix/lib
    $ ls
    
5: Run the wt_uhf_hub program in terminal:

        Prior to running, install JSON file from Google Cloud to allow permissions.
  
.. code-block:: terminal
  
    $ cd wt_uhf_hub
    $ python wt_uhf_hub.py
    
Dependancies
-------------
* Numpy
* Google Cloud
* pyserial
* PyBombs
* Adafruit-BBIO (1.0.9 or higher)

Features
--------
  
* TODO
 * Fill in documentation
 * Get PyBombs to install hackrf automatically
 * Make script to encrypt/decrypt JSON file

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
