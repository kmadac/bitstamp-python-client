import unittest

import bitstamp.client
import mock
import requests

from .fake_response import FakeResponse


class TradingTests(unittest.TestCase):

    def setUp(self):
        self.client = bitstamp.client.Trading('user', 'key', 'secret')

    def test_bad_response(self):
        response = FakeResponse(b'''{"error": "something went wrong"}''')
        with mock.patch('requests.post', return_value=response):
            self.assertRaises(
                bitstamp.client.BitstampError, self.client.account_balance)

    def test_404_response(self):
        response = FakeResponse(status_code=404)
        with mock.patch('requests.post', return_value=response):
            self.assertRaises(requests.HTTPError, self.client.account_balance)

    def test_500_response(self):
        response = FakeResponse(status_code=500)
        with mock.patch('requests.post', return_value=response):
            self.assertRaises(requests.HTTPError, self.client.account_balance)

    def test_account_balance(self):
        response = FakeResponse(b'''{
            "usd_balance": "100.00",
            "btc_balance": "2.001",
            "usd_reserved": "40",
            "btc_reserved": "1",
            "usd_available": "60.00",
            "btc_available": "1.001"}''')
        with mock.patch('requests.post', return_value=response):
            result = self.client.account_balance()
        self.assertIsInstance(result, dict)

    def test_user_transactions(self):
        response = FakeResponse(b'[]')
        with mock.patch('requests.post', return_value=response):
            result = self.client.user_transactions()
        self.assertIsInstance(result, list)

    def test_open_orders(self):
        response = FakeResponse(b'[]')
        with mock.patch('requests.post', return_value=response):
            result = self.client.open_orders()
        self.assertIsInstance(result, list)

    def test_bitcoin_deposit_address(self):
        response = FakeResponse(b'"1ARfAEqUzAtbnuJLUxm5KKfDJqrGi27hwA"')
        with mock.patch('requests.post', return_value=response):
            result = self.client.bitcoin_deposit_address()
        self.assertEqual(result, '1ARfAEqUzAtbnuJLUxm5KKfDJqrGi27hwA')

    # def test_buy_cancel_order(self):
    #     order_buy = self.client.buy_limit_order(1, 10)
    #     print(order_buy)
    #     self.assertIn('id', order_buy)
    #     order_id = order_buy['id']
    #     cancel_order = self.client.cancel_order(order_id)
    #     print(cancel_order)
    #     self.assertEqual(cancel_order, True)

    # def test_sell_cancel_order(self):
    #     order_sell = self.client.sell_limit_order(1, 500)
    #     print(order_sell)
    #     self.assertIn('id', order_sell)
    #     order_id = order_sell['id']
    #     cancel_order = self.client.cancel_order(order_id)
    #     print(cancel_order)
    #     self.assertEqual(cancel_order, True)

    # def test_withdrawal_requests(self):
    #     withdrawal_requests = self.client.withdrawal_requests()
    #     print(withdrawal_requests)
    #     self.assertIsInstance(withdrawal_requests, list)

    # def test_unconfirmed_bitcoin_deposits(self):
    #     unconfirmed_deposits = self.client.unconfirmed_bitcoin_deposits()
    #     print(unconfirmed_deposits)
    #     self.assertIsInstance(unconfirmed_deposits, list)


if __name__ == '__main__':
    unittest.main()
