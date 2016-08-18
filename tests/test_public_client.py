import unittest
import warnings

import bitstamp.client
import mock
import requests

from .fake_response import FakeResponse


class PublicTests(unittest.TestCase):

    def setUp(self):
        self.client = bitstamp.client.Public()

    def test_bad_response(self):
        response = FakeResponse(b'''{"error": "something went wrong"}''')
        with mock.patch('requests.get', return_value=response):
            self.assertRaises(
                bitstamp.client.BitstampError, self.client.ticker)

    def test_404_response(self):
        response = FakeResponse(status_code=404)
        with mock.patch('requests.get', return_value=response):
            self.assertRaises(requests.HTTPError, self.client.ticker)

    def test_500_response(self):
        response = FakeResponse(status_code=500)
        with mock.patch('requests.get', return_value=response):
            self.assertRaises(requests.HTTPError, self.client.ticker)

    def test_ticker(self):
        response = FakeResponse(b'''
            {"volume": "8700.01208078", "last": "816.44",
             "timestamp": "1390425002", "bid": "815.09", "high": "824.99",
             "low": "801.00", "ask": "816.44"}''')
        with mock.patch('requests.get', return_value=response):
            ticker = self.client.ticker()
        self.assertIsInstance(ticker, dict)

    def test_ticker_hour(self):
        response = FakeResponse(b'''
            {"volume": "8700.01208078", "last": "816.44",
             "timestamp": "1390425002", "bid": "815.09", "high": "824.99",
             "low": "801.00", "ask": "816.44"}''')
        with mock.patch('requests.get', return_value=response):
            ticker_hour = self.client.ticker_hour()
        self.assertIsInstance(ticker_hour, dict)

    def test_order_book(self):
        response = FakeResponse(b'''
            {"timestamp": "1390424821",
             "bids": [["817.22", "0.65814591"], ["814.92", "0.26999572"]],
             "asks": [["817.35", "0.04285277"], ["818.16", "0.03500000"]]}''')
        with mock.patch('requests.get', return_value=response):
            result = self.client.order_book(group=True)
        self.assertIsInstance(result, dict)
        self.assertEqual(sorted(result.keys()), ['asks', 'bids', 'timestamp'])

    def test_transactions(self):
        response = FakeResponse(b'''
            [{"date": "1390424582", "tid": 3176223, "price": "814.91",
              "amount": "1.65000000"},
             {"date": "1390424582", "tid": 3176222, "price": "815.00",
              "amount": "1.00000000"}]''')
        with mock.patch('requests.get', return_value=response):
            transactions = self.client.transactions()
        self.assertIsInstance(transactions, list)
        self.assertEqual(len(transactions), 2)

    def test_conversion_rate_usd_eur(self):
        response = FakeResponse(b'{"sell": "1.3500", "buy": "1.3611"}')
        with mock.patch('requests.get', return_value=response):
            result = self.client.conversion_rate_usd_eur()
        self.assertIsInstance(result, dict)
        self.assertEqual(sorted(result.keys()), ['buy', 'sell'])

        
class BackwardsCompatPublicTests(unittest.TestCase):

    def setUp(self):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.client = bitstamp.client.public()

    def test_deprecation_warning(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            self.assertRaises(DeprecationWarning, bitstamp.client.public)

    def test_bad_response(self):
        response = FakeResponse(b'''{"error": "something went wrong"}''')
        with mock.patch('requests.get', return_value=response):
            ticker = self.client.ticker()
        self.assertEqual(ticker, (False, 'something went wrong'))

    def test_500_response(self):
        response = FakeResponse(status_code=500)
        with mock.patch('requests.get', return_value=response):
            self.assertRaises(requests.HTTPError, self.client.ticker)


if __name__ == '__main__':
    unittest.main()
