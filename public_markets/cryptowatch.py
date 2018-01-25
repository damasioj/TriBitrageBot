import urllib.request
import urllib.error
import urllib.parse
import json
import config
import logging
from .market import Market

class Cryptowatch(Market):
    def __init__(self):
        super().__init__()
        self.depths = {}
        for pair in config.currency_pairs['all']:
            self.depths.update({pair : 'https://api.cryptowat.ch/markets/gdax/{}{}/orderbook'.format(pair[:3].lower(), pair[-3:].lower())})

    def update_depth(self):
        book = {}
        for pair in self.depths:
            url = self.depths[pair];
            req = urllib.request.Request(url,headers={
                "Content-Type": "application/json",
                "Accept": "*/*",
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36"})
            try:
                res = urllib.request.urlopen(req)
                depth = json.loads(res.read().decode('utf8'))
            except Exception as e:
                logging.error('Error getting market data:')
                logging.error(e)
                return book
            book.update({pair : self.format_depth(depth)})
        return book
        #print(self.depth)

    def sort_and_format(self, l): #format the ticker/trade
        l.sort(key=lambda x: float(x[1]))
        r = []
        for i in l:
            r.append({'price': float(i[0]), 'amount': float(i[1])})	
        return r

    def format_depth(self, depth):
        bids = depth['result']['bids']
        asks = depth['result']['asks']

        #bids = self.sort_and_format(depth['result']['bids'])
        #asks = self.sort_and_format(depth['result']['asks'])
        return {'asks':asks, 'bids':bids}
