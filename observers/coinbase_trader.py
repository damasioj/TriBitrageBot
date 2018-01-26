import sys
import os
import logging
import config
import time
from decimal import Decimal as dm
from .observer import Observer
from api_communicator import AuthenticatedClient

# how long to wait for order to fill
ORDER_EXPIRATION_TIME = 3

# Start communication with API, get start balance
comm = AuthenticatedClient(config.ACCESS_KEY, config.SECRET_KEY, config.PASSPHRASE)
for x in comm.get_accounts():
    if x['currency'] == config.currency_pref.upper():
        StartBalance = float(x['balance'])
        AccountID = x['id']
        logging.info('Account ID: {}'.format(AccountID))
        logging.info('Starting Balance: {} {}'.format(config.currency_pref, StartBalance))

TotalProfit = 0


class Coinbase_Trader(Observer):
    def opportunity(self, item, loggers):
        # case  btc -> usd -> eth -> btc
        logging.info('%s Amount %f Expected Profit %f' % (item[0][1]['case'], item[0][1]['amount'], item[0][1]['profit']))
        if item[0][1]['best_case'] == 1: 
            # get balance
            account = comm.get_account(AccountID)
            account['currency'] == config.currency_pref.upper()
            balance = float(account['available'])
            logging.info('Current Available Balance: {} {}'.format(config.currency_pref, balance))

            counter = 0
            while balance == 0 or item[0][1]['amount'] > balance:
                logging.info('Balance is 0. Waiting for replenishment...')
                counter += 1
                if counter > 2:
                    return
                time.sleep(1)
    
            # can be made into a for-loop. This way it will trade all pairs
            # make first trade
            logging.info('Step 1')
            trade = item[0][1]['best_trades'][0]
            logging.debug('Trade info: {}'.format(trade))
            commit_trade = self.perform_trade(trade), time.time()
            if 'message' in commit_trade[0]:
                logging.error('Error completing trading: {}'.format(commit_trade[0]['message']))
                return

            # make second trade
            logging.info('Step 2')
            trade = item[0][1]['best_trades'][1]
            logging.debug('Trade info: {}'.format(trade))
            if 'message' in commit_trade[0]:
                logging.error('Error completing trading: {}'.format(commit_trade[0]['message']))
                return     

            # make final trade
            logging.info('Step 3')
            trade = item[0][1]['best_trades'][2]
            logging.debug('Trade info: {}'.format(trade))
            if 'message' in commit_trade[0]:
                logging.error('Error completing trading: {}'.format(commit_trade[0]['message']))
                return   
            
            account = comm.get_account(AccountID)
            balance = float(account['balance'])
            self.TotalProfit = balance-StartBalance
            logging.info('New Balance: {} {}'.format(config.currency_pref, balance))    
            logging.info('Total profit: {} {}'.format(config.currency_pref, TotalProfit))

        if config.stop_bot_loss < 0: #incase user makes stop loss as negative number
            if self.TotalProfit <= config.stop_bot_loss:
                logging.error('Traded at loss. Terminating program.')
                os.sys("pause")
                sys.exit()
        elif self.TotalProfit <= config.stop_bot_loss * -1:
            logging.error('Traded at loss. Terminating program.')
            os.sys("pause")
            sys.exit()

    def recur(self, query_order):
        if 'status' in query_order.keys(): 
            if query_order['status'] == 'ok': 
                return True
            else:
                logging.warn('trade failed %s' % query_order['err-msg']) 
                return False  
        elif 'result' in query_order.keys():
            if query_order['result'] == 'success':
                return True
            else:
                logging.warn('trade failed %s' % query_order['message']) 
                return False             

    def perform_trade(self, trade):
        # format trade arguments
        do_trade = {'type' : config.order_type,
                    'side' : trade['type'],
                    'product_id' : '{}-{}'.format(trade['pair'][:3].upper(), trade['pair'][-3:].upper()),
                    'size' : trade['amount']}

        # commit trade
        query_order = comm.place_order(do_trade)
        return query_order

    # verify wallets to check for any leftover funds (due to GDAX 0.01 min_size)
    def check_wallets(self):
        for x in comm.get_accounts():
            if x['currency'] == 'ETH':
                eth_balance = float(x['balance'])
            if x['currency'] == 'LTC':
                ltc_balance = float(x['balance'])
            if x['currency'] == 'BTC':
                btc_balance = float(x['balance'])

        if eth_balance > 0.01:
            self.empty_currency('ETH-BTC', ethBalance)
        if btc_balance > 0.01:
            self.empty_currency('EUR-BTC', btcBalance)
        if ltc_balance >= 1.47:
            self.empty_currency('LTC-BTC', (ltcBalance-1.46))

    def empty_currency(self, pair, size):
        do_trade = {'type' : config.order_type,
                    'side' : 'sell',
                    'product_id' : pair,
                    'size' : size}

        # commit trade
        query_order = comm.place_order(do_trade)
        return query_order 
       


