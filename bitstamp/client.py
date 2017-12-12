from functools import wraps
import hmac
import hashlib
import time
import warnings

import requests


class BitstampError(Exception):
    pass


class TransRange(object):
    """
    Enum like object used in transaction method to specify time range
    from which to get list of transactions
    """
    HOUR = 'hour'
    MINUTE = 'minute'


class BaseClient(object):
    """
    A base class for the API Client methods that handles interaction with
    the requests library.
    """
    api_url = {1: 'https://www.bitstamp.net/api/',
               2: 'https://www.bitstamp.net/api/v2/'}
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

    def _construct_url(self, url, base, quote):
        """
        Adds the orderbook to the url if base and quote are specified.
        """
        if not base and not quote:
            return url
        else:
            url = url + base.lower() + quote.lower() + "/"
            return url

    def _request(self, func, url, version=1, *args, **kwargs):
        """
        Make a generic request, adding in any proxy defined by the instance.

        Raises a ``requests.HTTPError`` if the response status isn't 200, and
        raises a :class:`BitstampError` if the response contains a json encoded
        error message.
        """
        return_json = kwargs.pop('return_json', False)
        url = self.api_url[version] + url
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
            elif json_response.get('status') == "error":
                raise BitstampError(json_response.get('reason'))

        if return_json:
            if json_response is None:
                raise BitstampError(
                    "Could not decode json for: " + response.text)
            return json_response

        return response


class Public(BaseClient):

    def ticker(self, base="btc", quote="usd"):
        """
        Returns dictionary.
        """
        url = self._construct_url("ticker/", base, quote)
        return self._get(url, return_json=True, version=2)

    def ticker_hour(self, base="btc", quote="usd"):
        """
        Returns dictionary of the average ticker of the past hour.
        """
        url = self._construct_url("ticker_hour/", base, quote)
        return self._get(url, return_json=True, version=2)

    def order_book(self, group=True, base="btc", quote="usd"):
        """
        Returns dictionary with "bids" and "asks".

        Each is a list of open orders and each order is represented as a list
        of price and amount.
        """
        params = {'group': group}
        url = self._construct_url("order_book/", base, quote)
        return self._get(url, params=params, return_json=True, version=2)

    def transactions(self, time=TransRange.HOUR, base="btc", quote="usd"):
        """
        Returns transactions for the last 'timedelta' seconds.
        Parameter time is specified by one of two values of TransRange class.
        """
        params = {'time': time}
        url = self._construct_url("transactions/", base, quote)
        return self._get(url, params=params, return_json=True, version=2)

    def conversion_rate_usd_eur(self):
        """
        Returns simple dictionary::

            {'buy': 'buy conversion rate', 'sell': 'sell conversion rate'}
        """
        return self._get("eur_usd/", return_json=True, version=1)


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

    def account_balance(self, base="btc", quote="usd"):
        """
        Returns dictionary::

            {u'btc_reserved': u'0',
             u'fee': u'0.5000',
             u'btc_available': u'2.30856098',
             u'usd_reserved': u'0',
             u'btc_balance': u'2.30856098',
             u'usd_balance': u'114.64',
             u'usd_available': u'114.64',
             ---If base and quote were specified:
             u'fee': u'',
             ---If base and quote were not specified:
             u'btcusd_fee': u'0.25',
             u'btceur_fee': u'0.25',
             u'eurusd_fee': u'0.20',
             }
            There could be reasons to set base and quote to None (or False),
            because the result then will contain the fees for all currency pairs
            For backwards compatibility this can not be the default however.
        """
        url = self._construct_url("balance/", base, quote)
        return self._post(url, return_json=True, version=2)

    def user_transactions(self, offset=0, limit=100, descending=True,
                          base=None, quote=None):
        """
        Returns descending list of transactions. Every transaction (dictionary)
        contains::

            {u'usd': u'-39.25',
             u'datetime': u'2013-03-26 18:49:13',
             u'fee': u'0.20',
             u'btc': u'0.50000000',
             u'type': 2,
             u'id': 213642}

        Instead of the keys btc and usd, it can contain other currency codes
        """
        data = {
            'offset': offset,
            'limit': limit,
            'sort': 'desc' if descending else 'asc',
        }
        url = self._construct_url("user_transactions/", base, quote)
        return self._post(url, data=data, return_json=True, version=2)

    def open_orders(self, base="btc", quote="usd"):
        """
        Returns JSON list of open orders. Each order is represented as a
        dictionary.
        """
        url = self._construct_url("open_orders/", base, quote)
        return self._post(url, return_json=True, version=2)

    def order_status(self, order_id):
        """
        Returns dictionary.
        - status: 'Finished'
          or      'In Queue'
          or      'Open'
        - transactions: list of transactions
          Each transaction is a dictionary with the following keys:
              btc, usd, price, type, fee, datetime, tid
          or  btc, eur, ....
          or  eur, usd, ....
        """
        data = {'id': order_id}
        return self._post("order_status/", data=data, return_json=True,
                          version=1)

    def cancel_order(self, order_id, version=1):
        """
        Cancel the order specified by order_id.

        Version 1 (default for backwards compatibility reasons):
        Returns True if order was successfully canceled, otherwise
        raise a BitstampError.

        Version 2:
        Returns dictionary of the canceled order, containing the keys:
        id, type, price, amount
        """
        data = {'id': order_id}
        return self._post("cancel_order/", data=data, return_json=True,
                          version=version)

    def cancel_all_orders(self):
        """
        Cancel all open orders.

        Returns True if it was successful, otherwise raises a
        BitstampError.
        """
        return self._post("cancel_all_orders/", return_json=True, version=1)

    def buy_limit_order(self, amount, price, base="btc", quote="usd"):
        """
        Order to buy amount of bitcoins for specified price.
        """
        data = {'amount': amount, 'price': price}
        url = self._construct_url("buy/", base, quote)
        return self._post(url, data=data, return_json=True, version=2)

    def buy_market_order(self, amount, base="btc", quote="usd"):
        """
        Order to buy amount of bitcoins for market price.
        """
        data = {'amount': amount}
        url = self._construct_url("buy/market/", base, quote)
        return self._post(url, data=data, return_json=True, version=2)

    def sell_limit_order(self, amount, price, base="btc", quote="usd"):
        """
        Order to buy amount of bitcoins for specified price.
        """
        data = {'amount': amount, 'price': price}
        url = self._construct_url("sell/", base, quote)
        return self._post(url, data=data, return_json=True, version=2)

    def sell_market_order(self, amount, base="btc", quote="usd"):
        """
        Order to buy amount of bitcoins for market price.
        """
        data = {'amount': amount}
        url = self._construct_url("sell/market/", base, quote)
        return self._post(url, data=data, return_json=True, version=2)

    def check_bitstamp_code(self, code):
        """
        Returns JSON dictionary containing USD and BTC amount included in given
        bitstamp code.
        """
        data = {'code': code}
        return self._post("check_code/", data=data, return_json=True,
                          version=1)

    def redeem_bitstamp_code(self, code):
        """
        Returns JSON dictionary containing USD and BTC amount added to user's
        account.
        """
        data = {'code': code}
        return self._post("redeem_code/", data=data, return_json=True,
                          version=1)

    def withdrawal_requests(self):
        """
        Returns list of withdrawal requests.

        Each request is represented as a dictionary.
        """
        return self._post("withdrawal_requests/", return_json=True, version=1)

    def bitcoin_withdrawal(self, amount, address):
        """
        Send bitcoins to another bitcoin wallet specified by address.
        """
        data = {'amount': amount, 'address': address}
        return self._post("bitcoin_withdrawal/", data=data, return_json=True,
                          version=1)

    def bitcoin_deposit_address(self):
        """
        Returns bitcoin deposit address as unicode string
        """
        return self._post("bitcoin_deposit_address/", return_json=True,
                          version=1)

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
        return self._post("unconfirmed_btc/", return_json=True, version=1)

    def litecoin_withdrawal(self, amount, address):
        """
        Send litecoins to another litecoin wallet specified by address.
        """
        data = {'amount': amount, 'address': address}
        return self._post("ltc_withdrawal/", data=data, return_json=True,
                          version=2)

    def litecoin_deposit_address(self):
        """
        Returns litecoin deposit address as unicode string
        """
        return self._post("ltc_address/", return_json=True,
                          version=2)

    def ethereum_withdrawal(self, amount, address):
        """
        Send ethers to another ether wallet specified by address.
        """
        data = {'amount': amount, 'address': address}
        return self._post("eth_withdrawal/", data=data, return_json=True,
                          version=2)

    def ethereum_deposit_address(self):
        """
        Returns ethereum deposit address as unicode string
        """
        return self._post("eth_address/", return_json=True,
                          version=2)

    def ripple_withdrawal(self, amount, address, currency):
        """
        Returns true if successful.
        """
        data = {'amount': amount, 'address': address, 'currency': currency}
        response = self._post("ripple_withdrawal/", data=data,
                              return_json=True)
        return self._expect_true(response)

    def ripple_deposit_address(self):
        """
        Returns ripple deposit address as unicode string.
        """
        return self._post("ripple_address/", version=1, return_json=True)[
                          "address"]

    def xrp_withdrawal(self, amount, address, destination_tag=None):
        """
        Sends xrps to another xrp wallet specified by address. Returns withdrawal id.
        """
        data = {'amount': amount, 'address': address}
        if destination_tag:
            data['destination_tag'] = destination_tag

        return self._post("xrp_withdrawal/", data=data, return_json=True,
                          version=2)["id"]

    def xrp_deposit_address(self):
        """
        Returns ripple deposit address and destination tag as dictionary.
        Example: {u'destination_tag': 53965834, u'address': u'rDsbeamaa4FFwbQTJp9Rs84Q56vCiWCaBx'}

        """
        return self._post("xrp_address/", version=2, return_json=True)

    def transfer_to_main(self, amount, currency, subaccount=None):
        """
        Returns dictionary with status.
        subaccount has to be the numerical id of the subaccount, not the name
        """
        data = {'amount': amount,
                'currency': currency,}
        if subaccount is not None:
            data['subAccount'] = subaccount
        return self._post("transfer-to-main/", data=data, return_json=True,
                          version=2)

    def transfer_from_main(self, amount, currency, subaccount):
        """
        Returns dictionary with status.
        subaccount has to be the numerical id of the subaccount, not the name
        """
        data = {'amount': amount,
                'currency': currency,
                'subAccount': subaccount,}
        return self._post("transfer-from-main/", data=data, return_json=True,
                          version=2)


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
        Instantiate the wrapped class.
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
