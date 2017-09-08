import unittest

import bitstamp.client
import mock
import requests
import hmac
import hashlib

from .fake_response import FakeResponse


class TradingTests(unittest.TestCase):

    def setUp(self):
        self.username = 'USERNAME'
        self.key = 'KEY'
        self.secret = 'SECRET'
        self.client = bitstamp.client.Trading(
            self.username, self.key, self.secret)

    def test_bad_response(self):
        response = FakeResponse(b'''{"error": "something went wrong"}''')
        with mock.patch('requests.post', return_value=response):
            self.assertRaises(
                bitstamp.client.BitstampError, self.client.account_balance)

    def test_nonjson_response(self):
        response = FakeResponse(b'''Hey wait, this isn't JSON!''')
        with mock.patch('requests.post', return_value=response):
            self.assertRaises(
                bitstamp.client.BitstampError, self.client.account_balance)

    def test_404_response(self):
        response = FakeResponse(status_code=404)
        with mock.patch('requests.post', return_value=response):
            self.assertRaises(requests.HTTPError, self.client.account_balance)

    def test_nonce(self):
        # Each call to .nonce increases it.
        with mock.patch('time.time', return_value=1):
            self.assertEqual(self.client.get_nonce(), 1)
            self.assertEqual(self.client.get_nonce(), 2)
            self.assertEqual(self.client.get_nonce(), 3)
        # But if the unix time is greater, use that instead.
        with mock.patch('time.time', return_value=10):
            self.assertEqual(self.client.get_nonce(), 10)

    def test_500_response(self):
        response = FakeResponse(status_code=500)
        with mock.patch('requests.post', return_value=response):
            self.assertRaises(requests.HTTPError, self.client.account_balance)

    def test_signing(self):
        response = FakeResponse(b'[]')
        with mock.patch('requests.post', return_value=response) as mocker:
            self.client._post('test')
        kwargs = mocker.call_args[1]
        self.assertIn('data', kwargs)
        self.assertIn('nonce', kwargs['data'])
        self.assertIn('signature', kwargs['data'])
        self.assertEqual(kwargs['data'].get('key'), 'KEY')

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

    def test_order_status(self):
        response = FakeResponse(b'''{"status": "Open", "transactions": []}''')
        with mock.patch('requests.post', return_value=response):
            result = self.client.order_status(0000000000)
        self.assertIsInstance(result, dict)

    def test_bitcoin_deposit_address(self):
        response = FakeResponse(b'"1ARfAEqUzAtbnuJLUxm5KKfDJqrGi27hwA"')
        with mock.patch('requests.post', return_value=response):
            result = self.client.bitcoin_deposit_address()
        self.assertEqual(result, '1ARfAEqUzAtbnuJLUxm5KKfDJqrGi27hwA')

    def test_litecoin_deposit_address(self):
        response = FakeResponse(b'"MVYt6Mw6XHp7UE1gDn6pa8ZbsdtWqWiZUp"')
        with mock.patch('requests.post', return_value=response):
            result = self.client.litecoin_deposit_address()
        self.assertEqual(result, 'MVYt6Mw6XHp7UE1gDn6pa8ZbsdtWqWiZUp')

    def test_ethereum_deposit_address(self):
        response = FakeResponse(b'"0xbd8c4ffcb30c1fed0facf716bc9fd5849539e1c2"')
        with mock.patch('requests.post', return_value=response):
            result = self.client.ethereum_deposit_address()
        self.assertEqual(result, '0xbd8c4ffcb30c1fed0facf716bc9fd5849539e1c2')

    def test_buy_limit_order(self):
        response = FakeResponse(b'''
            {"amount": "0.1",
             "datetime": "2014-01-22 01:20:23.226788",
             "id": 55507211,
             "price": "90",
             "type": 0}''')
        with mock.patch('requests.post', return_value=response):
            result = self.client.buy_limit_order('0.1', '90')
        self.assertIsInstance(result, dict)

    def test_sell_limit_order(self):
        response = FakeResponse(b'''
            {"amount": "1",
             "datetime": "2014-01-22 02:20:23.226788",
             "id": 55507212,
             "price": "9000",
             "type": 1}''')
        with mock.patch('requests.post', return_value=response):
            result = self.client.sell_limit_order('1', '9000')
        self.assertIsInstance(result, dict)

    def test_buy_market_order(self):
        response = FakeResponse(b'''
            {"amount": "0.1",
             "datetime": "2014-01-22 01:20:23.226788",
             "id": 55507211,
             "price": "90",
             "type": 0}''')
        with mock.patch('requests.post', return_value=response):
            result = self.client.buy_market_order('0.1')
        self.assertIsInstance(result, dict)

    def test_sell_market_order(self):
        response = FakeResponse(b'''
            {"amount": "1",
             "datetime": "2014-01-22 02:20:23.226788",
             "id": 55507212,
             "price": "9000",
             "type": 1}''')
        with mock.patch('requests.post', return_value=response):
            result = self.client.sell_market_order('1')
        self.assertIsInstance(result, dict)

    def test_cancel_order(self):
        response = FakeResponse(b'true')
        with mock.patch('requests.post', return_value=response):
            result = self.client.cancel_order('15807214')
        self.assertTrue(result)

    def test_cancel_order_v2(self):
        response = FakeResponse(b'{}')
        with mock.patch('requests.post', return_value=response):
            result = self.client.cancel_order('15807214', version=2)
        self.assertIsInstance(result, dict)

    def test_cancel_all_orders(self):
        response = FakeResponse(b'true')
        with mock.patch('requests.post', return_value=response):
            result = self.client.cancel_all_orders()
        self.assertTrue(result)

    def test_withdrawal_requests(self):
        response = FakeResponse(b'[]')
        with mock.patch('requests.post', return_value=response):
            result = self.client.withdrawal_requests()
        self.assertIsInstance(result, list)

    def test_unconfirmed_bitcoin_deposits(self):
        response = FakeResponse(b'[]')
        with mock.patch('requests.post', return_value=response):
            result = self.client.unconfirmed_bitcoin_deposits()
        self.assertIsInstance(result, list)

    def test_default_data(self):
        """
        GitHub Issue #9
        """
        ret_data = self.client._default_data()
        msg = str(ret_data['nonce']) + self.username + self.key
        signature = hmac.new(
            self.secret.encode('utf-8'), msg=msg.encode('utf-8'),
            digestmod=hashlib.sha256).hexdigest().upper()
        self.assertEqual(signature, ret_data['signature'])

    def test_bitcoin_withdrawal(self):
        response = FakeResponse(b'''{"id": "1"}''')
        with mock.patch('requests.post', return_value=response):
            result = self.client.unconfirmed_bitcoin_deposits()
        self.assertIsInstance(result, dict)

    def test_transfer_to_main(self):
        response = FakeResponse(b'{"status": "ok"}')
        with mock.patch('requests.post', return_value=response):
            result = self.client.transfer_to_main(1, "btc")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "ok")

    def test_transfer_from_main(self):
        response = FakeResponse(b'{"status": "ok"}')
        with mock.patch('requests.post', return_value=response):
            result = self.client.transfer_from_main(1, "btc", "")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["status"], "ok")


if __name__ == '__main__':
    unittest.main()
