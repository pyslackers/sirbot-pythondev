======================================
Pyslackers Sir-bot-a-lot configuration
======================================

|build|

`Sir-bot-a-lot`_ configuration for the people and by the people of the
`python developers slack community`_.

Want to join? `Get an invite`_ !

.. _Get an invite: http://pythondevelopers.herokuapp.com/
.. _python developers slack community: https://pythondev.slack.com/
.. _sir-bot-a-lot: http://sir-bot-a-lot.readthedocs.io/en/latest/
.. |build| image:: https://travis-ci.org/pyslackers/sirbot-pythondev.svg?branch=master
    :alt: Build status
    :target: https://travis-ci.org/pyslackers/sirbot-pythondev

Getting started
---------------

Docker & ngrok
^^^^^^^^^^^^^^

The easiest way to get started is by using docker-compose with the
``docker-compose.ngrok.yml`` file.

1. `Install docker & docker-compose`_.

2. Clone and cd in the repository.

    $ git clone https://github.com/pyslackers/sirbot-pythondev.git && cd sirbot-pythondev

3. Copy & rename the ``docker/.env.example`` to ``docker/.env``.

4. Set your environment variable in ``docker/.env``.

5. Start the containers with:

    $ docker-compose -f docker/docker-compose.ngrok.yml up --build

6. Sir Bot-a-lot is now started and the ngrok web interface is available
at: ``http://localhost:8000``.

.. _Install docker & docker-compose: https://docs.docker.com/compose/install/
