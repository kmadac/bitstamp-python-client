__author__ = 'kmadac'

import unittest
import bitstamp.client


class bitstamp_public_TestCase(unittest.TestCase):
    def setUp(self):
        self.client = bitstamp.client.public()

    def test_ticker(self):
        ticker = self.client.ticker()
        print(ticker)
        self.assertIsInstance(ticker, dict)

    def test_order_book(self):
        order_book = self.client.order_book(group=True)
        print(order_book)
        self.assertIsInstance(order_book, dict)

    def test_transactions(self):
        transactions = self.client.transactions()
        print(transactions)
        self.assertIsInstance(transactions, list)

    def test_bitinstant_reserves(self):
        bitinstant_reserves = self.client.bitinstant_reserves()
        print(bitinstant_reserves)
        self.assertIsInstance(bitinstant_reserves, dict)

    def test_conversion_rate_usd_eur(self):
        conversion_rate_usd_eur = self.client.conversion_rate_usd_eur()
        print (conversion_rate_usd_eur)
        self.assertIsInstance(conversion_rate_usd_eur, dict)

if __name__ == '__main__':
    unittest.main()
