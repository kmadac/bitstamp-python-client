from functools import wraps
import hmac
import hashlib
import time
import warnings

import requests


class BitstampError(Exception):
    pass


class BaseClient(object):
    """
    A base class for the API Client methods that handles interaction with
    the requests library.
    """
    api_url = 'https://www.bitstamp.net/api/'
    exception_on_error = True

    def __init__(self, proxydict=None, *args, **kwargs):
        self.proxydict = proxydict

    def _get(self, *args, **kwargs):
        """
        Make a GET request.
        """
        return self._request(requests.get, *args, **kwargs)

    def _post(self, *args, **kwargs):
        """
        Make a POST request.
        """
        data = self._default_data()
        data.update(kwargs.get('data') or {})
        kwargs['data'] = data
        return self._request(requests.post, *args, **kwargs)

    def _default_data(self):
        """
        Default data for a POST request.
        """
        return {}

    def _request(self, func, url, *args, **kwargs):
        """
        Make a generic request, adding in any proxy defined by the instance.

        Raises a ``requests.HTTPError`` if the response status isn't 200, and
        raises a :class:`BitstampError` if the response contains a json encoded
        error message.
        """
        return_json = kwargs.pop('return_json', False)
        url = self.api_url + url
        response = func(url, *args, **kwargs)

        if 'proxies' not in kwargs:
            kwargs['proxies'] = self.proxydict

        # Check for error, raising an exception if appropriate.
        response.raise_for_status()

        try:
            json_response = response.json()
        except ValueError:
            json_response = None
        if isinstance(json_response, dict):
            error = json_response.get('error')
            if error:
                raise BitstampError(error)

        if return_json:
            if json_response is None:
                raise BitstampError(
                    "Could not decode json for: " + response.text)
            return json_response

        return response


class Public(BaseClient):

    def ticker(self):
        """
        Returns dictionary.
        """
        return self._get("ticker/", return_json=True)

    def order_book(self, group=True):
        """
        Returns dictionary with "bids" and "asks".

        Each is a list of open orders and each order is represented as a list
        of price and amount.
        """
        params = {'group': group}
        return self._get("order_book/", params=params, return_json=True)

    def transactions(self, timedelta_secs=86400):
        """
        Returns transactions for the last 'timedelta' seconds.
        """
        params = {'timedelta': timedelta_secs}
        return self._get("transactions/", params=params, return_json=True)

    def conversion_rate_usd_eur(self):
        """
        Returns simple dictionary::

            {'buy': 'buy conversion rate', 'sell': 'sell conversion rate'}
        """
        return self._get("eur_usd/", return_json=True)


class Trading(Public):

    def __init__(self, username, key, secret, *args, **kwargs):
        """
        Stores the username, key, and secret which is used when making POST
        requests to Bitstamp.
        """
        super(Trading, self).__init__(
            username=username, key=key, secret=secret, *args, **kwargs)
        self.username = username
        self.key = key
        self.secret = secret

    def get_nonce(self):
        """
        Get a unique nonce for the bitstamp API.

        This integer must always be increasing, so use the current unix time.
        Every time this variable is requested, it automatically increments to
        allow for more than one API request per second.

        This isn't a thread-safe function however, so you should only rely on a
        single thread if you have a high level of concurrent API requests in
        your application.
        """
        nonce = getattr(self, '_nonce', 0)
        if nonce:
            nonce += 1
        # If the unix time is greater though, use that instead (helps low
        # concurrency multi-threaded apps always call with the largest nonce).
        self._nonce = max(int(time.time()), nonce)
        return self._nonce

    def _default_data(self, *args, **kwargs):
        """
        Generate a one-time signature and other data required to send a secure
        POST request to the Bitstamp API.
        """
        data = super(Trading, self)._default_data(*args, **kwargs)
        data['key'] = self.key
        nonce = self.get_nonce()
        msg = str(nonce) + self.username + self.key

        signature = hmac.new(
            self.secret.encode('utf-8'), msg=msg.encode('utf-8'),
            digestmod=hashlib.sha256).hexdigest().upper()
        data['signature'] = signature
        data['nonce'] = nonce
        return data

    def _expect_true(self, response):
        """
        A shortcut that raises a :class:`BitstampError` if the response didn't
        just contain the text 'true'.
        """
        if response.text == u'true':
            return True
        raise BitstampError("Unexpected response")

    def account_balance(self):
        """
        Returns dictionary::

            {u'btc_reserved': u'0',
             u'fee': u'0.5000',
             u'btc_available': u'2.30856098',
             u'usd_reserved': u'0',
             u'btc_balance': u'2.30856098',
             u'usd_balance': u'114.64',
             u'usd_available': u'114.64'}
        """
        return self._post("balance/", return_json=True)

    def user_transactions(self, offset=0, limit=100, descending=True):
        """
        Returns descending list of transactions. Every transaction (dictionary)
        contains::

            {u'usd': u'-39.25',
             u'datetime': u'2013-03-26 18:49:13',
             u'fee': u'0.20', u'btc': u'0.50000000',
             u'type': 2,
             u'id': 213642}
        """
        data = {
            'offset': offset,
            'limit': limit,
            'sort': 'desc' if descending else 'asc',
        }
        return self._post("user_transactions/", data=data, return_json=True)

    def open_orders(self):
        """
        Returns JSON list of open orders. Each order is represented as a
        dictionary.
        """
        return self._post("open_orders/", return_json=True)

    def cancel_order(self, order_id):
        """
        Cancel the order specified by order_id.

        Returns True if order was successfully canceled,otherwise raise a
        BitstampError.
        """
        data = {'id': order_id}
        return self._post("cancel_order/", data=data, return_json=True)

    def buy_limit_order(self, amount, price):
        """
        Order to buy amount of bitcoins for specified price.
        """
        data = {'amount': amount, 'price': price}

        return self._post("buy/", data=data, return_json=True)

    def sell_limit_order(self, amount, price):
        """
        Order to buy amount of bitcoins for specified price.
        """
        data = {'amount': amount, 'price': price}
        return self._post("sell/", data=data, return_json=True)

    def check_bitstamp_code(self, code):
        """
        Returns JSON dictionary containing USD and BTC amount included in given
        bitstamp code.
        """
        data = {'code': code}
        return self._post("check_code/", data=data, return_json=True)

    def redeem_bitstamp_code(self, code):
        """
        Returns JSON dictionary containing USD and BTC amount added to user's
        account.
        """
        data = {'code': code}
        return self._post("redeem_code/", data=data, return_json=True)

    def withdrawal_requests(self):
        """
        Returns list of withdrawal requests.

        Each request is represented as a dictionary.
        """
        return self._post("withdrawal_requests/", return_json=True)

    def bitcoin_withdrawal(self, amount, address):
        """
        Send bitcoins to another bitcoin wallet specified by address.
        """
        data = {'amount': amount, 'address': address}
        return self._post("bitcoin_withdrawal/", data=data, return_json=True)

    def bitcoin_deposit_address(self):
        """
        Returns bitcoin deposit address as unicode string
        """
        return self._post("bitcoin_deposit_address/", return_json=True)

    def unconfirmed_bitcoin_deposits(self):
        """
        Returns JSON list of unconfirmed bitcoin transactions.

        Each transaction is represented as dictionary:

        amount
          bitcoin amount
        address
          deposit address used
        confirmations
          number of confirmations
        """
        return self._post("unconfirmed_btc/", return_json=True)

    def ripple_withdrawal(self, amount, address, currency):
        """
        Returns true if successful.
        """
        data = {'amount': amount, 'address': address, 'currency': currency}
        response = requests.post("ripple_withdrawal/", data=data)
        return self._expect_true(response)

    def ripple_deposit_address(self):
        """
        Returns ripple deposit address as unicode string.
        """
        return requests.post("ripple_address/").text


# Backwards compatibility
class BackwardsCompat(object):
    """
    Version 1 used lower case class names that didn't raise an exception when
    Bitstamp returned a response indicating an error had occured.

    Instead, it returned a tuple containing ``(False, 'The error message')``.
    """
    wrapped_class = None

    def __init__(self, *args, **kwargs):
        """
        Instanciate the wrapped class.
        """
        self.wrapped = self.wrapped_class(*args, **kwargs)
        class_name = self.__class__.__name__
        warnings.warn(
            "Use the {} class rather than the deprecated {} one".format(
                class_name.title(), class_name),
            DeprecationWarning, stacklevel=2)

    def __getattr__(self, name):
        """
        Return the wrapped attribute. If it's a callable then return the error
        tuple when appropriate.
        """
        attr = getattr(self.wrapped, name)
        if not callable(attr):
            return attr

        @wraps(attr)
        def wrapped_callable(*args, **kwargs):
            """
            Catch ``BitstampError`` and replace with the tuple error pair.
            """
            try:
                return attr(*args, **kwargs)
            except BitstampError as e:
                return False, e.args[0]

        return wrapped_callable


class public(BackwardsCompat):
    """
    Deprecated version 1 client. Use :class:`Public` instead.
    """
    wrapped_class = Public


class trading(BackwardsCompat):
    """
    Deprecated version 1 client. Use :class:`Trading` instead.
    """
    wrapped_class = Trading
