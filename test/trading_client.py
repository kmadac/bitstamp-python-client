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

    def test_buy_cancel(self):
        pass
#    def test_cancel_order(self):
#        cancel_order = self.client.cancel_order(123)
#        print cancel_order
#        self.assertEquals(True, False)

if __name__ == '__main__':
    unittest.main()
