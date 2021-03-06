Note for using OpenGL 3.2
-------------------------
You will have to override the on_resize event or else your program will crash,
because the default one of Pyglet calls OpenGL functions that are not
available anymore in OpenGL 3.2.
It may look something like this:
```python
@window.event
def on_resize(width, height):
    return pyglet.event.EVENT_HANDLED
```

pyglet
======

http://www.pyglet.org/

pyglet provides an object-oriented programming interface for developing games
and other visually-rich applications for Windows, Mac OS X and Linux.

Requirements
------------

pyglet runs with Python 2.5+ and also with Python 3 through 2to3 tool (which
is executed automatically when installing). pyglet works on the following
operating systems:

* Windows XP or later
* Mac OS X 10.3 or later
* Linux, with the following libraries (most recent distributions will have
  these in a default installation):
    * OpenGL and GLX
    * GDK 2.0 or later (required for loading images)
    * OpenAL or ALSA (required for playing audio)
    
Installation
------------

If you're reading this README from a source distribution, install pyglet
with::

    python setup.py install

There are no compilation steps during the installation; if you prefer, you can
simply add this directory to your PYTHONPATH and use pyglet without
installing it.

Support
-------

pyglet has an active developer and user community.  If you find a bug, please
open an issue at http://code.google.com/p/pyglet/issues (requires a Google
account).

Please join us on the mailing list at 
http://groups.google.com/group/pyglet-users

For more information and an RSS news feed, visit http://www.pyglet.org

Testing
-------

Because of its interactive nature pyglet uses a custom test runner which is
invoked with:

    % python tests/test.py

The test runner is described in more detail in the tests/test.py docstring.
