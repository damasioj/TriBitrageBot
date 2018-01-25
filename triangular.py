import config
import sys
import os
import logging
import time
from concurrent.futures import ThreadPoolExecutor, wait

class Triangular():
    def __init__(self):
        self.observers = []
        self.symbols = config.symbols
        self.bookData = []
        self.threadpool = ThreadPoolExecutor(max_workers=1) # number of symbols
        self.init_observers(config.observers)
        self.init_market(config.market)

    def init_observers(self, _observers):
        if config.demo_mode:
            try:
                exec('import observers.logger')
                observer = eval('observers.logger.Logger()')
                self.observers.append(observer)
                logging.info('Initialized demo bot ...')
            except(ImportError, AttributeError) as e:
                logging.error('Couldn\'t initialize demo bot. Are you missing files?')  
                logging.error('Error message: {}'.format(e))
        else:
            for observer_name in _observers: 
                try:
                    exec('import observers.' + observer_name.lower())
                    observer = eval('observers.' + observer_name.lower() + '.' + observer_name + '()')
                    self.observers.append(observer)
                    logging.info('Initialized bots ...')
                except(ImportError, AttributeError) as e:
                    logging.error('%s observer name is invalid. Please verify config file.' % observer_name)  
                    logging.error('Error message: {}'.format(e))  

    def init_market(self, market):
        try:
            exec('import public_markets.' + market.lower())
            m = eval('public_markets.' + market.lower() + '.' + market + '()' )
            self.market = m
        except(ImportError, AttributeError) as e:
            print('%s market name is invalid' % m)

    def __get_triangle_pairs(self):
        pairs = []
        first = config.currency_pref
        second = ''
        third = ''
        numOfPairs = len(config.currency_pairs['all']) - 1
        for pair in config.currency_pairs['all']:
            if first in pair:
                if first in pair[:3]:
                    second = pair[-3:]
                else:
                    second = pair[:3]
            else:
                continue
            while True:
                for pair2 in config.currency_pairs['all']:
                    if second in pair2 and first not in pair2:
                        if second in pair2[:3]:
                            third = pair2[-3:]
                            while True:
                                for pair3 in config.currency_pairs['all']:
                                    if third in pair3 and first in pair3:
                                        pairs.append([pair, pair2, pair3])
                                    if config.currency_pairs['all'].index(pair3) == numOfPairs:
                                        break
                                if config.currency_pairs['all'].index(pair3) == numOfPairs:
                                        break
                        else:
                            third = pair2[:3]
                            while True:
                                for pair3 in config.currency_pairs['all']:
                                    if third in pair3 and first in pair3:
                                        pairs.append([pair, pair2, pair3])
                                    if config.currency_pairs['all'].index(pair3) == numOfPairs:
                                        break
                                if config.currency_pairs['all'].index(pair3) == numOfPairs:
                                        break
                    if config.currency_pairs['all'].index(pair2) == numOfPairs:
                        break
                if config.currency_pairs['all'].index(pair2) == numOfPairs:
                        break
        logging.info('------------------------------------------------------')
        logging.info('---------------------TRIANGLES------------------------')
        for i in pairs:
            logging.info(i)
        logging.info('------------------------------------------------------')
        return pairs          

    def __get_triangle_results(self, pairs, results):
        results[','.join(pairs)] = Triangle(pairs, self.bookData).main()

    def _get_market_data(self):
        self.bookData = self.market.update_depth()
        if self.bookData != {}:
            logging.info('----------------------PRICES-------------------------')
            for item in self.bookData:
                logging.info('{} : {:0.4f}'.format(item, ((self.bookData[item]['bids'][0][0] + self.bookData[item]['asks'][0][0]) / 2))) 
            logging.info('-----------------------------------------------------')

    def update_cases(self, triangles):
        futures = []
        results = {}
        #results = self.__get_triangle_results(triangles[0]) #for testing
        for pairs in triangles:
            futures.append(self.threadpool.submit(self.__get_triangle_results, pairs, results))
        wait(futures, timeout=4)
        return results
                
    def loop(self):
        triangles = self.__get_triangle_pairs()
        while True:
            if not config.demo_mode:
                self.observers[0].check_wallets()
            self._get_market_data()
            if self.bookData != {}:
                config.market_reset_time = 0
                self.triangles = self.update_cases(triangles)
                logging.info('-----------------------------------------------------')
                item = sorted(self.triangles.items(), key=lambda x: x[1]['profit'], reverse=True)
                if item != [] and item[0][1]['profit'] > 0:
                    for pair in item:
                        if pair[1]['profit'] > 0:
                            item2 = [(pair[0], pair[1])] #simplifying item dict
                            for observer in self.observers:
                                observer.opportunity(item2)  
                        else:
                            logging.info('-----------------------------------------------------')
                            break
                else:
                    logging.info('No opportunity found.')
                    logging.info('-----------------------------------------------------')
                time.sleep(config.refresh_rate + config.market_reset_time)


class Triangle():
    def __init__(self, pairs, data):
        self.fee = config.fee
        self.slippage = config.slippage
        self.triangle_pairs = pairs
        self.data = data #ticker data
        self.depths = {}
        self.threadpool = ThreadPoolExecutor(max_workers=3) # number of pairs in the symbol  

    def get_data(self): #get only related triangles
        depths = {}
        for pair in self.data:
            if self.triangle_pairs[0] in pair or self.triangle_pairs[1] in pair or self.triangle_pairs[2] in pair:
                depths.update({pair : self.data[pair]})
        return depths

    def pricer(self, orders, amount, side):
        vol = 0
        value = 0
        i = 0
        amount = amount - (amount * self.fee)

        if side == 'buy':
            while i < len(orders['asks']) and value < amount: #check if amount being bought is larger than trade size
                this_value = min(orders['asks'][i]['price'] * orders['asks'][i]['amount'], amount - value) # get total amount being sold
                this_vol = this_value / orders['asks'][i]['price'] # convert currency
                value += this_value
                vol += this_vol
                i += 1
            return (value / vol, vol)

        else:
            while i < len(orders['bids']) and value < amount:
                this_value = min(orders['bids'][i]['amount'], amount - value)
                this_vol = this_value * orders['bids'][i]['price']
                value += this_value
                vol += this_vol
                i += 1
            return (value, vol)
       
    def main(self):
        self.depths = self.get_data()

        firstTickOrders = self.depths[self.triangle_pairs[0]]
        secondTickOrders = self.depths[self.triangle_pairs[1]]
        thirdTickOrders = self.depths[self.triangle_pairs[2]]
        
        amt = config.min_amount
        best_case = 0
        while amt <= config.max_amount:
            #=============================== CASE 1
            #Used to define the flow of the trade
            #True = bid price, False = ask price
            #For example: Ticker BTCUSD means price is in USD and bid would mean buying BTC
            #If we want to sell BTC. We need ask price for first phase.
            firstProduct = config.currency_pref
            phaseOne = 'buy'
            phaseTwo = 'buy'
            phaseThree = 'buy'

            if firstProduct in self.triangle_pairs[0][:3]:
                phaseOne = 'sell'
            if self.triangle_pairs[1][:3] in self.triangle_pairs[0]:
                phaseTwo = 'sell'
            if self.triangle_pairs[2][:3] in self.triangle_pairs[1]:
                phaseThree = 'sell'
            
            #case 1: btc -> 2nd product -> 3rd product -> btc
            firstBalance = self.pricer(firstTickOrders, amt, phaseOne)
            secondBalance = self.pricer(secondTickOrders, firstBalance[1], phaseTwo)
            finalBalance = self.pricer(thirdTickOrders, secondBalance[1], phaseThree)
            
            best_profit = 0
            c1_profit = finalBalance[1] - amt
            c1_profit_percent = (c1_profit / amt) * 100
            
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


