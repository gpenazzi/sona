SONA
=====

sona is a small code I wrote for fun to play noise generators in python.
The idea is to have indefinite sound/noise generator which can be modified in real time using pyAudio as audio backend.

The generators can be played directly or they can through a threaded player.
In this way we are able to change the attributes of the generator from the python console and modify the noise in real time.

Command line usage
--------------

For the available arguments:

.. code-block::

	$ sona --help

To generate a brown noise (default exponent 2.0);

.. code-block::

	$ sona colored_noise

Interactive usage
--------------

You can play a generator directly from console. For example, to play a pulse generator:

.. code-block::

	>>> import sona
	>>> g = sona.PulseGenerator()  # The generator
	>>> player = sona.Player(g)    # The player
	>>> player.start()

Now the generator is playing. You can interact with it changing its attributes.
For example:

.. code-block::

	>>> g.distance /= 2.0  # More frequent pulses

Stop the player:

.. code-block::

	>>> player.stop()


License
--------
Sona is distributed under BSD license.
