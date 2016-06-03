check_travis - Icinga/Nagios + Travis
=====================================

This is small plugin for checking Travis_ build status. Example icinga2
config is available in ``/usr/share/doc/check_travis``. Services are
configured like such::

    object Host "travis-ci" {
        address = "api.travis-ci.org"
        check_command = "http"
        vars.http_vhost = "$address$"
        vars.http_ssl = true

        vars.travis_repos["travis-ci/travis-api"] = {}
        vars.travis_repos["QubesOS/qubes-core-admin"] = {}
    }

.. _Travis: https://www.travis-ci.org/

Installation
------------

::

    python3 setup.py install
    cp /usr/share/doc/check_travis/icinga2.conf /etc/icinga2/conf.d/travis.conf

Author
------

Wojtek Porczyk ``woju invisiblethingslab com``
