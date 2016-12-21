curlrc
======

.. image:: https://travis-ci.org/benwebber/curlrc.svg?branch=master
    :target: https://travis-ci.org/benwebber/curlrc

Treat curl configuration files as ``curlrc`` subcommands.

Usage
-----

curl can read arguments from a `configuration file`_. You can use this mechanism to specify default arguments (as ``~/.curlrc``), or tell curl to read arguments from a specific file::

    curl -K @/path/to/config.rc

Create a few config files and drop them in ``~/.curl`` (or ``$CURL_HOME`` if set)::

    ~/.curl
    └── example.rc

``curlrc`` exposes configuration files as subcommands::

    $ curlrc example

If the configuration file includes an `output template`_, you can reformat the data
as CSV, tab-separated columns, or JSON::

    $ curlrc example -f csv https://example.org
    $ curlrc example -f table https://example.org
    $ curlrc example -f json https://example.org

Any options you pass to ``curlrc`` after ``--`` will be passed to curl::

    $ curlrc example -- -fsSL https://example.org

Example
-------

Consider the following configuration file::

    # output timing data
    -s
    -S
    -o = /dev/null
    -w = "url_effective: %{url_effective}\ntime_namelookup: %{time_namelookup}\ntime_connect: %{time_connect}\ntime_appconnect: %{time_appconnect}\ntime_pretransfer: %{time_pretransfer}\ntime_redirect: %{time_redirect}\ntime_starttransfer: %{time_starttransfer}\ntime_total: %{time_total}\n"

If you drop this in ``~/.curl/time.rc`` (or ``$CURL_HOME/time.rc``), you can use it by calling ``curlrc time``::

    $ curlrc time https://example.org
    url_effective: https://example.org/
    time_namelookup: 0.001
    time_connect: 0.026
    time_appconnect: 0.180
    time_pretransfer: 0.180
    time_redirect: 0.000
    time_starttransfer: 0.210
    time_total: 0.210

Don't like the default format? Try CSV::

    $ curlrc time -f csv https://example.org
    url_effective,time_namelookup,time_connect,time_appconnect,time_pretransfer,time_redirect,time_starttransfer,time_total
    https://example.org/,0.001,0.030,0.194,0.194,0.000,0.228,0.228

or tab-separated columns::

    $ curlrc time -f table https://example.org
    url_effective	https://example.org/
    time_namelookup	0.002
    time_connect	0.028
    time_appconnect	0.177
    time_pretransfer	0.177
    time_redirect	0.000
    time_starttransfer	0.205
    time_total	0.206

or even JSON::

    $ curlrc time -f json https://example.org
    {
      "url_effective": "https://example.org/", 
      "time_namelookup": "0.001", 
      "time_connect": "0.028", 
      "time_appconnect": "0.182", 
      "time_pretransfer": "0.182", 
      "time_redirect": "0.000", 
      "time_starttransfer": "0.213", 
      "time_total": "0.213"
    }

Installation
------------

``curlrc`` requires Python 2.7 or later. It only depends on the standard library.

Download the `latest release`_ or install with pip:

.. code-block:: bash

    pip install curlrc

Licence
-------

MIT

.. _configuration file: http://curl.haxx.se/docs/manpage.html#-K
.. _output template: http://curl.haxx.se/docs/manpage.html#-w
.. _latest release: https://github.com/benwebber/curlrc/releases/latest
