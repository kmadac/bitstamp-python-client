.. image:: https://travis-ci.org/kmadac/bitstamp-python-client.svg?branch=master
    :target: https://travis-ci.org/kmadac/bitstamp-python-client

======================
bitstamp-python-client
======================

Python package to communicate with the bitstamp.net API (v1 and v2).

Compatible with Python 2.7+ and Python 3.3+


Overview
========

There are two classes. One for the public part of API and a second for the
trading part.

Public class doesn't need user credentials, because API commands which this
class implements are not bound to bitstamp user account.

Description of API: https://www.bitstamp.net/api/


Install
=======

Install from PyPi::

    pip install BitstampClient

Install from git::

    pip install git+git://github.com/kmadac/bitstamp-python-client.git


Usage
=====

Here's a quick example of usage::

    >>> import bitstamp.client

    >>> public_client = bitstamp.client.Public()
    >>> print(public_client.ticker()['volume'])
    8700.01208078

    >>> trading_client = bitstamp.client.Trading(
    ...     username='999999', key='xxx', secret='xxx')
    >>> print(trading_client.account_balance()['fee'])
    0.5000
    >>> print(trading_client.ticker()['volume'])   # Can access public methods
    8700.01208078



How to activate a new API key
=============================

1. Login your Bitstamp account

2. Click on Security -> Api Access

3. Select permissions which you want to have for you access key (if you don't
   check any box, you will get error message 'No permission found' after each
   API call)

4. Click the 'Generate key' button and don't forget to write down your Secret!

5. Click 'Activate'

6. Goto your Inbox and click on link sent by Bitstamp to activate this API key


Class diagram
=============
.. image:: https://raw.github.com/kmadac/bitstamp-python-client/master/class_diagram.png
   :alt: Class diagram
   :align: center
