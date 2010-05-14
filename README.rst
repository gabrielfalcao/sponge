!! IMPORTANT !!
===============

    this project is no longer maintained, since I've figured out I
    Django is the way to go :)

Sponge - Web Framework
======================

Sponge is a tiny web framework build on top of CherryPy_.
Its name came from the idea of getting things dry.

Goals
=====

Be very well documented, often released, and 100% tested, as well.

Dependencies
============

 * CherryPy_ >= 3.1.1
 * Genshi_ >= 0.5.1
 * nose_ >= 0.11.0
 * mox_ >= 0.5.1

Documentation
=============

The documentation is bundle in the project, but you can see it online_.

Installing
==========

Debian GNU/Linux
^^^^^^^^^^^^^^^^

If you are running Debian with unstable repositories, just run::
   sudo aptitude install python-sponge

In other systems
^^^^^^^^^^^^^^^^
On unix-based systems::
   sudo python setup.py install

On windows::
   python setup.py install


Contributing
============

With new features
^^^^^^^^^^^^^^^^^

 1. Create both unit and functional tests for your new feature
 2. Do not let the coverage go down, 100% is the minimum.
 3. Write properly documentation
 4. Send-me a patch with: ``git format-patch``

Fixing bugs
^^^^^^^^^^^

 1. Create unit and/or functional tests to proof the bug you are fixing
 2. Do not let the coverage go down, 100% is the minimum.
 3. Send-me a patch with: ``git format-patch``

.. _CherryPy: http://www.cherrypy.org/
.. _Genshi: http://genshi.edgewall.org/
.. _nose: http://code.google.com/p/python-nose/
.. _mox: http://code.google.com/p/pymox/test
.. _online: http://gnu.gabrielfalcao.com/projects/sponge/tutorial.html

