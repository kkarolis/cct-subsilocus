Subsilocus
----------
|Python Version| |License| |Code Style|

Subsidium Locus (or Subsilocus for short) is a room reservation service which
exposes an API to manage rooms/employees/reservations. It enforces employees to
create non-overlapping reservations so that sanity can be in-check.

Behind the scenes, `Django Rest Framework
<https://www.django-rest-framework.org/>`_ is used.

.. |Python Version| image:: https://img.shields.io/badge/python-3.8-blue
.. |License| image:: https://img.shields.io/github/license/kkarolis/cct-subsilocus
.. |Code Style| image:: https://img.shields.io/badge/code%20style-black-000000.svg

Requirements
------------

`Docker <www.docker.com>`_ and `Docker Compose
<https://docs.docker.com/compose/>`_ are required to run the local dockerized
version of the software.  Tested with the following versions:

``Docker version 19.03.5-ce, build 633a0ea838``

``docker-compose version 1.25.0``

No guarantees it will work with different versions of the aforementioned software.

Quickstart (Demo)
-----------------

In order to quickly demo the service some demo data is provided under ``demo`` directory named ``demo.json``

.. code:: bash

    docker-compose run --service-ports --rm subsilocus loaddata demo/demo.json
    docker-compose run --service-ports --rm subsilocus

This will load the database with 3 users, 2 meeting rooms, 2 employees and 6
reservations happening in the distant future. The demo user credentials (which
will be needed later) are (in format ``$username / $password``):

.. code:: 
    
    admin / admin
    john / john
    bill / bill

Authentication
^^^^^^^^^^^^^^

Both `SessionAuthentication
<https://www.django-rest-framework.org/api-guide/authentication/#sessionauthentication>`_
and `TokenAuthentication
<https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication>`_
authentication methods can be used to authenticate with this service.


Possible Actions
^^^^^^^^^^^^^^^^

All of the actions are listed in the Discoverable api (if running locally via
Quickstart service will be available `<http://localhost:8000>`_) provided by
Django Rest Framework.

For testing the service from command line, `Curlie
<https://github.com/rs/curlie>`_ can be used. Some examples are given below:

.. code:: bash

    # generate/get api token for demo user bill
    curlie -L POST http://localhost:8000/api-token-auth/ username=bill password=bill

    # create a meeting room
    curlie -L --user bill:bill POST http://localhost:8000/meeting-rooms/ name="Room"

    # create a employee
    curlie -L --user bill:bill POST http://localhost:8000/employees/ name="Employee"

    # should be executed inside this repository (or demo/make_reservation.json path changed)
    # fallback to curl for this
    curl -v --user bill:bill -X POST -H "Content-Type: application/json" \
        -d @demo/make_reservation.json http://localhost:8000/reservations/

    # cancel a reservation
    curlie -L --user bill:bill POST http://localhost:8000/reservations/8/cancel/


Assumptions / Limitations
-------------------------

- No easy way to create a new user (requires going to django shell)
- Employee is unrelated from the user using the API
- Reservations can be made in the past (its assumed this could be used for
  logging past reservations)
- No access controls for who can view what / who can modify what
- API was not test with invalid (non unicode data)

    
Development
-----------

Test can be run via command:

.. code::

    docker-compose run --service-ports --rm subsilocus test
