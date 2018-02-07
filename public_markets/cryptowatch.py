import urllib.request
import urllib.error
import urllib.parse
import json
import config
import logging
from .market import Market


class Cryptowatch(Market):
    def __init__(self, logger):
        #super().__init__()
        self.depths = {}
        self.logger = logger[0]
        market = config.market if config.market != 'Coinbase' else 'gdax'
        for pair in config.currency_pairs[config.symbols]:
            self.depths.update({pair : 'https://api.cryptowat.ch/markets/{}/{}/orderbook'.format(market.lower(),
                                                                                                 pair.lower())})

    def update_depth(self):
        book = {}
        allowance = 0
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
            allowance = depth['allowance']['remaining']
            book.update({pair : self.format_depth(depth)})
        self.logger.info('Allowance left: {}'.format(allowance))
        return book

    # format and sort book
    # the book has to be in the following format to work with triangular class:
    # book['bids/asks'][x]['price/amount']
    def sort_and_format(self, section):
        #l.sort(key=lambda x: float(x[1]))
        section_formatted = []
        for i in section:
            section_formatted.append({'price': float(i[0]), 'amount': float(i[1])})
        return section_formatted

    def format_depth(self, depth):
        bids = self.sort_and_format(depth['result']['bids'])
        asks = self.sort_and_format(depth['result']['asks'])

        if bids[0]['price'] == 0:
            bids[0] = bids[1:]
        if asks[0]['price'] == 0:
            asks = asks[1:]
            
        return {'asks':asks, 'bids':bids}
