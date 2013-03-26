__author__ = 'kmadac'

import requests


class public():
    def ticker(self):
        """
        Return dictionary
        """
        r = requests.get("https://www.bitstamp.net/api/ticker/")
        if r.status_code == 200:
            return r.json()
        else:
            r.raise_for_status()

    def order_book(self, group=True):
        """
        Returns JSON dictionary with "bids" and "asks".
        Each is a list of open orders and each order is represented as a list of price and amount.
        """
        params = {'group': group}

        r = requests.get("https://www.bitstamp.net/api/order_book/", params=params)
        if r.status_code == 200:
            return r.json()
        else:
            r.raise_for_status()

    def transactions(self, timedelta_secs=86400):
        """
        Returns transactions for the last 'timedelta' seconds
        """
        params = {'timedelta': timedelta_secs}

        r = requests.get("https://www.bitstamp.net/api/transactions/", params=params)
        if r.status_code == 200:
            return r.json()
        else:
            r.raise_for_status()

    def bitinstant_reserves(self):
        """
        Returns simple dictionary {'usd': 'Bitinstant USD reserves'}
        """
        r = requests.get("https://www.bitstamp.net/api/bitinstant/")
        if r.status_code == 200:
            return r.json()
        else:
            r.raise_for_status()

    def conversion_rate_usd_eur(self):
        """
        Returns simple dictionary
        {'buy': 'buy conversion rate', 'sell': 'sell conversion rate'}
        """
        r = requests.get("https://www.bitstamp.net/api/eur_usd/")
        if r.status_code == 200:
            return r.json()
        else:
            r.raise_for_status()


class trading():
    def __init__(self, user, password):
        self.params = {'user': user, 'password': password}

    def account_ballance(self):
        """
        Returns dictionary:
        {u'btc_reserved': u'0',
         u'fee': u'0.5000',
         u'btc_available': u'2.30856098',
         u'usd_reserved': u'0',
         u'btc_balance': u'2.30856098',
         u'usd_balance': u'114.64',
         u'usd_available': u'114.64'}
        """
        r = requests.post("https://www.bitstamp.net/api/balance/", data=self.params)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.json()
        else:
            r.raise_for_status()

    def user_transactions(self, timedelta_secs=86400):
        """
        Returns descending list of transactions. Every transaction (dictionary) contains
        {u'usd': u'-39.25',
         u'datetime': u'2013-03-26 18:49:13',
         u'fee': u'0.20', u'btc': u'0.50000000',
         u'type': 2,
         u'id': 213642}
        """
        self.params['timedelta'] = timedelta_secs

        r = requests.post("https://www.bitstamp.net/api/user_transactions/", data=self.params)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.json()
        else:
            r.raise_for_status()

    def open_orders(self):
        """
        Returns JSON list of open orders. Each order is represented as dictionary:

        """
        r = requests.post("https://www.bitstamp.net/api/open_orders/", data=self.params)
        if r.status_code == 200:
            if 'error' in r.json():
                return False, r.json()['error']
            else:
                return r.json()
        else:
            r.raise_for_status()