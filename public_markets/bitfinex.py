import urllib.request
import urllib.error
import urllib.parse
import json
import os
import config
from .market import Market

class Bitfinex(Market):
    def __init__(self):
        super().__init__()
##        self.depths = {
##            'btcusd' : 'https://api.bitfinex.com/v2/book/tBTCUSD/P0',
##            'ethusd' : 'https://api.bitfinex.com/v2/book/tETHUSD/P0',
##            'ethbtc' : 'https://api.bitfinex.com/v2/book/tETHBTC/P0',
##        }

    def format_depths_url(self): #add pair formatting here to send as link
        pairList = ''
        first = True
        for pair in config.currency_pairs['all']:
                if first:
                        pairList = 't{}'.format(pair.upper())
                        first = False
                else:
                        pairList = '{},t{}'.format(pairList, pair.upper())
        url = 'https://api.bitfinex.com/v2/tickers?symbols={}'.format(pairList)
        return url
                

    def update_depth(self):
        #url = self.depths[symbol];
        url = self.format_depths_url()
        req = urllib.request.Request(url,headers={
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36"})
        res = urllib.request.urlopen(req)
        depth = json.loads(res.read().decode('utf8'))
        self.format(depth)
        return depth

##    def sort_and_format(self, l, reverse): #format the ticker/trade
##        l.sort(key=lambda x: float(x[0]), reverse=reverse)        
##        r = []
##        for i in l:
##            if i[2] < 0:
##                i[2] = i[2] * - 1
##            r.append({'price': float(i[0]), 'amount': float(i[2])})     #define the price of the ticker and the amount
##        return r

    def format(self, depth): #format tickers text
            charList = []
            for item in depth:
                item[0] = item[0][1:]

##    def format_depth(self, depth):
##                
##        bids = self.sort_and_format(depth[:24], True) #send bid for formatting
##        asks = self.sort_and_format(depth[25:], False) #send ask for formatting
##        
##        return marketData
