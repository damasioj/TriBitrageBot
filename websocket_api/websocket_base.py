import gdax
import logging
from decimal import *

max_amount = 0
orderbook = {}

class WebsocketClient_GDAX(gdax.WebsocketClient):
    def __init_base__(self, max_amount):
        self.max_amount = max_amount

    def __init_logger__(self, logger):
        self.logger = logger
        self.logger.info("Websocket logger initialized.")
    
    def on_message(self, msg):
        # create order book
        if msg['type'] == 'snapshot':
            self.orderbook = {"bids": msg['bids'], "asks": msg['asks']}
            self.logger.info("BIDS: " + str(msg['bids'][0]), "ASKS: " + str(msg['asks'][0]))
            return

        # update orderbook
        if msg['type'] == 'l2update':
            value = round(float(msg['changes'][0][1]), 2)

            if 'buy' in msg['changes'][0]:
                for offer in self.orderbook['bids']:
                    itemIndex = 0

                    # try to find and update index
                    if value in offer:
                        itemIndex = self.orderbook['bids'].index(offer)
                        if msg['changes'][0][2] == 0:
                            del self.orderbook['bids'][itemIndex]
                            self.logger.info("Deleted from orderbook: ASKS, Value: " + str(value))
                        else:
                            self.orderbook['bids'][itemIndex][2] == msg['changes'][0][2]
                            self.logger.info("Updated orderbook: ASKS: " + self.orderbook['bids'][itemIndex])
                        return

                    # add new index
                    if float(offer[1]) > value:
                        self.orderbook['bids'].insert(itemIndex, [msg['changes'][0][0], value, msg['changes'][0][2]])
                        
                    itemIndex = self.orderbook['bids'].index(offer)
                    return
                self.logger.info("Something went wrong...")

            elif 'sell' in msg['changes'][0]:
                self.logger.info("Sale")
                return

        # type not handled
        self.logger.info(msg)
