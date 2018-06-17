import config
import sys
import os
import logging
import logging.config
import time
import gdax
import json
from concurrent.futures import ThreadPoolExecutor, wait


class Triangular():
    #loggerList = []
    
    def __init__(self):
        self.observers = []
        self.public_market = ''
        self.symbols = config.symbols
        self.bookData = []
        self.loggerList = []
        self.init_logger()
        self.threadpool = ThreadPoolExecutor(max_workers=1) # number of symbols
        self.init_observers(config.observers)
        self.init_market(config.market, config.sec_markets, config.socket)
        self.loggerList[0].info('Utilizing {} symbols'.format(config.symbols))
        self.use_primary_market = True
        self.time_awaited = 0

    def init_observers(self, _observers):
        if config.demo_mode:
            try:
                self.loggerList[0].info('Initializing demo bot ...')
                exec('import observers.logger')
                observer = eval('observers.logger.Logger()')
                self.observers.append(observer)
                self.loggerList[0].info('Finished initializing demo bot.')
            except(ImportError, AttributeError) as e:
                self.loggerList[0].error('Couldn\'t initialize demo bot. Are you missing files?')
                self.loggerList[0].error('Error message: {}'.format(e))
        else:
            for observer_name in _observers: 
                self.loggerList[0].info('Initializing production bots ...')
                try:
                    exec('import observers.' + observer_name.lower())
                    observer = eval('observers.' + observer_name.lower() + '.' + observer_name + '()')
                    self.observers.append(observer)
                    self.loggerList[0].info('Finished initializing bot: {}'.format(observer_name))
                except(ImportError, AttributeError) as e:
                    self.loggerList[0].error('%s observer name is invalid. Please verify config file.' % observer_name)  
                    self.loggerList[0].error('Error message: {}'.format(e))  

    def init_market(self, market, secondary_markets, socket=""):
        self.loggerList[0].info('Launching public markets ...')
        self.market = []
        try:
            self.loggerList[0].info("Starting public socket")
            self.market.append(gdax.WebsocketClient(url="wss://ws-feed.gdax.com", products="BTC-EUR"))
            self.market.append(gdax.OrderBook("BTC-EUR"))
            return
            
            exec('import public_markets.' + market.lower() + ', public_markets.cryptowatch')

            # import market
            main = eval('public_markets.' + market.lower() + '.' + market + '(self.loggerList)')
            self.market.append(main)
            self.loggerList[0].info('Finished importing public market: {}'.format(market))

            # import secondary market sources
            for site in secondary_markets:
                secondary = eval('public_markets.' + site.lower() + '.' + site + '(self.loggerList)')
                self.market.append(secondary)
                self.loggerList[0].info('Finished importing public market: {}'.format(site))
        except(ImportError, AttributeError) as e:
            self.loggerList[0].error('Failed to import public market.')
            self.loggerList[0].error('Error: {}'.format(e))

    def init_logger(self):
        logging.config.fileConfig('logger.config')
        logger = logging.getLogger('main_logger')
        o_logger = logging.getLogger('opportunity_logger')
        self.loggerList = [logger, o_logger]

    def __get_triangle_pairs(self):
        # gets all possible triangle pairs in the given list of symbols from config.currency_pairs
        pairs = []
        first = config.currency_pref
        numOfPairs = len(config.currency_pairs[config.symbols]) - 1
        for pair in config.currency_pairs[config.symbols]:
            if first in pair:
                if first in pair[:3]:
                    second = pair[-3:]
                else:
                    second = pair[:3]
            else:
                continue
            while True:
                for pair2 in config.currency_pairs[config.symbols]:
                    if second in pair2 and first not in pair2:
                        if second in pair2[:3]:
                            third = pair2[-3:]
                            while True:
                                for pair3 in config.currency_pairs[config.symbols]:
                                    if third in pair3 and first in pair3:
                                        pairs.append([pair, pair2, pair3])
                                    if config.currency_pairs[config.symbols].index(pair3) == numOfPairs:
                                        break
                                if config.currency_pairs[config.symbols].index(pair3) == numOfPairs:
                                        break
                        else:
                            third = pair2[:3]
                            while True:
                                for pair3 in config.currency_pairs[config.symbols]:
                                    if third in pair3 and first in pair3:
                                        pairs.append([pair, pair2, pair3])
                                    if config.currency_pairs[config.symbols].index(pair3) == numOfPairs:
                                        break
                                if config.currency_pairs[config.symbols].index(pair3) == numOfPairs:
                                        break
                    if config.currency_pairs[config.symbols].index(pair2) == numOfPairs:
                        break
                if config.currency_pairs[config.symbols].index(pair2) == numOfPairs:
                        break
        self.loggerList[0].info('------------------------------------------------------')
        self.loggerList[0].info('---------------------TRIANGLES------------------------')
        for i in pairs:
            self.loggerList[0].info(i)
        self.loggerList[0].info('------------------------------------------------------')
        return pairs          

    def __get_triangle_results(self, pairs, results):
        results[','.join(pairs)] = Triangle(pairs, self.bookData).main(self.loggerList)

    def _get_market_data(self):
        if self.use_primary_market:
            self.bookData = self.market[0].update_depth()
        else:
            self.bookData = self.market[1].update_depth()
        if self.bookData != {}:
            self.loggerList[0].info('----------------------PRICES-------------------------')
            for item in self.bookData:
                self.loggerList[0].info('{} : {:0.4f}'.format(item, ((self.bookData[item]['bids'][0]['price'] +
                                                                      self.bookData[item]['asks'][0]['price']) / 2)))
            self.loggerList[0].info('-----------------------------------------------------')
        else:
            self.use_primary_market = False # alternate to secondary market
            self.time_awaited = time.time()

    def update_cases(self, triangles):
        futures = []
        results = {}
        #results = self.__get_triangle_results(triangles[0]) #for testing
        self.loggerList[0].debug('----------------------RESULTS------------------------')
        for pairs in triangles:
            futures.append(self.threadpool.submit(self.__get_triangle_results, pairs, results))
        wait(futures, timeout=3)
        return results
                
    def loop(self):
        if time.time() - self.time_awaited < config.market_expiration_time:
            self.use_primary_market = True
        triangles = self.__get_triangle_pairs()
        self.market[0].start() # starts main socket
        self.market[1].start() # starts order book socket                               
        while True:
            if not config.demo_mode:
                self.observers[0].check_wallets()

            #self._get_market_data()
            time.sleep(5)
            self.loggerList[0].info("Order book: " + str(self.market[1].get_ask()))
            #self.loggerList[0].info("Main: " + self.market[0].
            time.sleep(10)
            self.market[0].close()
            self.market[1].close()
            if self.bookData != {}:
                self.triangles = self.update_cases(triangles)
                self.loggerList[0].info('-----------------------------------------------------')
                item = sorted(self.triangles.items(), key=lambda x: x[1]['profit'], reverse=True)
                if item != [] and item[0][1]['profit'] > 0:
                    for pair in item:
                        if pair[1]['profit'] > 0:
                            item2 = [(pair[0], pair[1])] # simplifying item dict
                            for observer in self.observers:
                                observer.opportunity(item2, self.loggerList)
                        else:
                            self.loggerList[0].info('-----------------------------------------------------')
                            self.loggerList[1].info('-----------------------------------------------------')
                            break
                else:
                    self.loggerList[0].info('No opportunity found.')
                    self.loggerList[0].info('-----------------------------------------------------')
                time.sleep(config.refresh_rate)



class Triangle():
    def __init__(self, pairs, data):
        self.fee = config.fee
        self.slippage = config.slippage
        self.triangle_pairs = pairs
        self.data = data # ticker data
        self.depths = {}
        self.threadpool = ThreadPoolExecutor(max_workers=3) # number of pairs in the symbol

    def get_data(self): # get only related triangles
        depths = {}
        for pair in self.data:
            if self.triangle_pairs[0] in pair or self.triangle_pairs[1] in pair or self.triangle_pairs[2] in pair:
                depths.update({pair : self.data[pair]})
        return depths

    def pricer(self, triangle, amount, side, fee):
        vol = 0
        value = 0
        i = 0
        prepay = False

        # used in cases where the fee must be discounted from the amount bought (i.e. bitfinex model)
        if config.market.lower() == 'bitfinex':
            prepay = True
            amount = amount - (amount * self.fee)

        if side == 'buy':
            while i < len(self.depths[triangle]['asks']) and value < amount: # check if amount being bought is larger than trade size
                this_value = min(self.depths[triangle]['asks'][i]['price'] * self.depths[triangle]['asks'][i]['amount'], amount - value) # get total amount being sold
                this_vol = this_value / self.depths[triangle]['asks'][i]['price'] # convert currency
                value += this_value
                vol += this_vol
                i += 1
            if prepay:
                return value / vol, vol
            return value / vol, vol - (vol * fee)

        else:
            while i < len(self.depths[triangle]['bids']) and value < amount:
                this_value = min(self.depths[triangle]['bids'][i]['amount'], amount - value)
                this_vol = this_value * self.depths[triangle]['bids'][i]['price']
                value += this_value
                vol += this_vol
                i += 1
            if prepay:
                return value, vol
            return value, vol - (vol * fee)
       
    def main(self, logger):
        self.depths = self.get_data()

        # Used to define the flow of the trade
        phases = ['buy', 'buy', 'buy']
        firstProduct = config.currency_pref
        if firstProduct in self.triangle_pairs[0][:3]:
            phases[0] = 'sell'
        if self.triangle_pairs[1][:3] in self.triangle_pairs[0]:
            phases[1] = 'sell'
        if self.triangle_pairs[2][:3] in self.triangle_pairs[1]:
            phases[2] = 'sell'

        amt = config.min_amount
        best_case = 0
        results = []
        while amt <= config.max_amount:

            # calculate final balance
            balance = amt
            for i in range(3):
                # check if using gdax and current trade is btceur
                if self.triangle_pairs[i] == 'btceur' and config.market.lower() == 'coinbase':
                    fee = 0.0025
                else:
                    fee = self.fee

                new_balance = self.pricer(self.triangle_pairs[i], balance, phases[i], fee)
                balance = new_balance[1]
            
            best_profit = 0
            c1_profit = balance - amt
            c1_profit_percent = (c1_profit / amt) * 100

            results.append(round(c1_profit_percent, 2))

            if (c1_profit_percent / 100) > config.min_profit:
                best_case = 1
                best_profit = c1_profit
                best_amount = amt - (amt * config.fee)
                best_trades = [
                    {
                        'pair':self.triangle_pairs[0],
                        'type':phaseOne,
                        'amount':round(best_amount, 2),
                        #'rate':round(firstTicker[phaseOne[1]], 6)
                    },    
                    {
                        'pair':self.triangle_pairs[1],
                        'type':'buy',
                        'amount':round(firstBalance[1], 2),
                        #'rate':round(secondTicker[phaseTwo[1]], 6)
                    },
                    {
                        'pair':self.triangle_pairs[2],
                        'type':'sell',
                        'amount':round(secondBalance[1], 2),
                        #'rate':round(thirdTicker[phaseThree[1]], 6)
                    },
                ]
            
            amt += config.increment

        # used to display results for debugging
        logger[0].debug(' ** {} :'.format(self.triangle_pairs))
        logger[0].debug(' ** ** {}'.format(results))

        if best_case > 0:
            case = "{} -> {} -> {}".format(self.triangle_pairs[0], self.triangle_pairs[1], self.triangle_pairs[2]) if best_case == 1 else "{} -> {} -> {}".format(self.triangle_pairs[0], self.triangle_pairs[1], self.triangle_pairs[2])                
            return {
                'case':case,
                'amount':best_amount,
                'profit':best_profit,
                'best_trades':best_trades,
                'best_case':best_case
            }  

        return {
            'case':0,
            'amount':0,
            'profit':0,
            'best_trades':[],
            'best_case':0
        }                                               


