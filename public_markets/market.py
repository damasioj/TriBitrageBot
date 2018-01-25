import time
import urllib.request
import urllib.error
import urllib.parse
import config
import logging
from utils import log_exception

class Market():
    def __init__(self):
        self.name = self.__class__.__name__
        self.depth_updated = 0
        self.update_rate = 3

    def get_depth(self, pair):
        timediff = time.time() - self.depth_updated
        if timediff > self.update_rate:
            valid = self.ask_update_depth(pair)
        timediff = time.time() - self.depth_updated

        if timediff > config.market_expiration_time:
            logging.warn('Market: %s order book is expired' % self.name)
            self.depth = {}
        elif not valid:
            logging.warn('Market: %s cannot be accessed' % self.name)
            self.depth = {}
        return self.depth

    def ask_update_depth(self, pair):
        try:
            self.update_depth(pair)
            self.depth_updated = time.time()
        except Exception as e:
            logging.debug("HTTPError, can't update market: %s" % self.name)
            #log_exception(logging.DEBUG)
            self.depth_updated = time.time() + config.market_reset_time
            return False
        return True
        
    def update_depth(self):
        pass

    def buy(self, price, amount):
        pass

    def sell(self, price, amount):
        pass                   



            
            

