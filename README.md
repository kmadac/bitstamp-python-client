bitstamp-python-client
======================

Python package to communicate with bitstamp.net API

## Overview ##

There are two classes. One for public part of API and second for trading part.
Public class doesn't need user credentials, because API commands which this class implements are not bound to bitstamp user account.

Description of API:
https://www.bitstamp.net/api/

### Package requirements ###

* requests (pip install requests)

### Install from Git ###

    sudo pip install git+git://github.com/kmadac/bitstamp-python-client.git

### Following methods are not implemented yet ###

* Create Bitstamp code
* Check Bitstamp code
* Redeem Bitstamp code
* Send to user

### Usage example ###

    import bitstamp.client
    bs_client_public = bitstamp.client.public()
    ticker = bs_client_public.ticker()

    bs_client_trading = bitstamp.client.trading(user='999999', password='yoursecret')
    account_balance = bs_client_trading.account_ballance()

### If this code is usable for you, here is my wallet id where you can contribute to my work with few micro BCs: ###

## 159bihAxJTKNsJSvCxYgAHKd8UX7kJugUQ ##
