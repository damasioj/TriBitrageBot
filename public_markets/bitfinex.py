import urllib.request
import urllib.error
import urllib.parse
import json
import os
import config
from .market import Market


class Bitfinex(Market):
    def __init__(self, logger):
        #super().__init__()
        self.depths = {}
        self.logger = logger[0]
        for pair in config.currency_pairs['bitfinex']:
            self.depths.update({pair : 'https://api.bitfinex.com/v1/book/{}'.format(pair.lower())})

    def update_depth(self):
        book = {}
        for symbol in self.depths:
            url = self.depths[symbol]
            req = urllib.request.Request(url,headers={
                "Content-Type": "application/json",
                "Accept": "*/*",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36"})
            try:
                res = urllib.request.urlopen(req)
                depth = json.loads(res.read().decode('utf8'))
            except Exception as e:
                self.logger.error('Error getting market data:')
                self.logger.error(e)
                return book
            book.update({symbol : self.format_depth(depth)})
        return book

    # format and sort book
    # the book has to be in the following format to work with triangular class:
    # book['bids/asks'][x]['price/amount']
    def sort_and_format(self, l, reverse):
        # l.sort(key=lambda x: float(x[0]), reverse=reverse)
        r = []
        for i in l:
            r.append({'price': float(i['price']), 'amount': float(i['amount'])})
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['bids'], True) #send bid for formatting
        asks = self.sort_and_format(depth['asks'], False) #send ask for formatting

        return {'bids':bids, 'asks':asks}
