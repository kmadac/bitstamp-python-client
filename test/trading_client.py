__author__ = 'kmadac'

import unittest
import bitstamp.client
import os


class bitstamp_trading_TestCase(unittest.TestCase):
    client = bitstamp.client.trading(os.environ['bs_user'], os.environ['bs_key'], os.environ['bs_secret'])

    def test_account_ballance(self):
        account_balance = self.client.account_balance()
        print(account_balance)
        self.assertIsInstance(account_balance, dict)

    def test_user_transactions(self):
        user_transactions = self.client.user_transactions()
        print(user_transactions)
        self.assertIsInstance(user_transactions, list)

    def test_open_orders(self):
        open_orders = self.client.open_orders()
        print(open_orders)
        self.assertIsInstance(open_orders, list)

    def test_bitcoin_deposit_address(self):
        bitcoin_deposit_address = self.client.bitcoin_deposit_address()
        print(bitcoin_deposit_address)
        self.assertEquals(bitcoin_deposit_address, u'"1ARfAEqUzAtbnuJLUxm5KKfDJqrGi27hwA"')

    def test_buy_cancel_order(self):
        order_buy = self.client.buy_limit_order(1, 10)
        print(order_buy)
        self.assertIn('id', order_buy)
        order_id = order_buy['id']
        cancel_order = self.client.cancel_order(order_id)
        print(cancel_order)
        self.assertEquals(cancel_order, True)

    def test_sell_cancel_order(self):
        order_sell = self.client.sell_limit_order(1, 500)
        print (order_sell)
        self.assertIn('id', order_sell)
        order_id = order_sell['id']
        cancel_order = self.client.cancel_order(order_id)
        print (cancel_order)
        self.assertEquals(cancel_order, True)

    def test_withdrawal_requests(self):
        withdrawal_requests = self.client.withdrawal_requests()
        print(withdrawal_requests)
        self.assertIsInstance(withdrawal_requests, list)

    def test_unconfirmed_bitcoin_deposits(self):
        unconfirmed_deposits = self.client.unconfirmed_bitcoin_deposits()
        print(unconfirmed_deposits)
        self.assertIsInstance(unconfirmed_deposits, list)

if __name__ == '__main__':
    unittest.main()
