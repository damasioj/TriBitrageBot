import urllib.request
import urllib.error
import urllib.parse
import json
import config
import logging
from .market import Market

class Coinbase(Market):
    def __init__(self, logger):
        #super().__init__()
        self.depths = {}
        self.logger = logger[0]
        for pair in config.currency_pairs['gdax']:
            self.depths.update({pair : 'https://api.gdax.com/products/{}-{}/book?level=2'.format(pair[:3].upper(), pair[-3:].upper())})

    def update_depth(self):
        book = {}
        for pair in self.depths:
            url = self.depths[pair]
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
            book.update({pair : self.format_depth(depth)})
        return book
        #print(self.depth)

    def sort_and_format(self, l): #format the ticker/trade
        #l.sort(key=lambda x: float(x[0]))
        r = []
        for i in l:
            r.append({'price': float(i[0]), 'amount': float(i[1])})	
        return r

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['bids'])
        asks = self.sort_and_format(depth['asks'])
        return {'asks':asks, 'bids':bids}
