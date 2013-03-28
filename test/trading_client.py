__author__ = 'kmadac'

import unittest
import bitstamp.client
import os


class bitstamp_trading_TestCase(unittest.TestCase):
    def setUp(self):
        self.client = bitstamp.client.trading(os.environ['bs_user'], os.environ['bs_pass'])

    def test_account_ballance(self):
        account_ballance = self.client.account_ballance()
        print account_ballance
        self.assertIsInstance(account_ballance, dict)

    def test_user_transactions(self):
        user_transactions = self.client.user_transactions()
        print user_transactions
        self.assertIsInstance(user_transactions, list)

    def test_open_orders(self):
        open_orders = self.client.open_orders()
        print open_orders
        self.assertIsInstance(open_orders, list)

    def test_bitcoin_deposit_address(self):
        bitcoin_deposit_address = self.client.bitcoin_deposit_address()
        print bitcoin_deposit_address
        self.assertEquals(bitcoin_deposit_address, u'"1ARfAEqUzAtbnuJLUxm5KKfDJqrGi27hwA"')

    def test_buy_cancel_order(self):
        order_buy = self.client.buy_limit_order(1, 10)
        print order_buy
        self.assertIn('id', order_buy)
        order_id = order_buy['id']
        cancel_order = self.client.cancel_order(order_id)
        print cancel_order
        self.assertEquals(cancel_order, True)

if __name__ == '__main__':
    unittest.main()
