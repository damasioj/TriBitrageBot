import sys
import logging
import config
import time
import os
from .observer import Observer
from api_communicator import Client

# how long to wait for order to fill
ORDER_EXPIRATION_TIME = 3

#Start communication with API, get start balance
comm = Client()
for x in comm.balances():
    if x['type'] == config.wallet_type and x['currency'] == config.currency_pref:
        StartBalance = float(x['amount'])
        logging.info('Starting Balance: {} {}'.format(config.currency_pref, StartBalance))

TotalProfit = 0

class TraderBot_Finex(Observer):
    def opportunity(self, item):
        #case 2: btc -> usd -> eth -> btc
        logging.info('%s Amount %f Expected Profit %f' % (item[0][1]['case'], item[0][1]['amount'], item[0][1]['profit']))
        if item[0][1]['best_case'] == 1: 
            #get balance
            balance = 0
            for x in comm.balances():
                if x['type'] == config.wallet_type and x['currency'] == config.currency_pref:
                    balance = float(x['available'])
                    logging.info('Current Available Balance: %s %.5f' % (config.currency_pref, balance))
            
            counter = 0
            while balance == 0 or item[0][1]['amount'] > balance:
                logging.info('Balance is 0. Waiting for replenishment...')
                counter += 1
                if counter > 2:
                    return
                time.sleep(1)

            #can be made into a for-loop. This way it will trade all pairs
            #make first trade
            logging.info('Step 1')
            trade = item[0][1]['best_trades'][0]
            logging.debug('Trade info: {}'.format(trade))
            commit_trade = self.perform_trade(trade,False), time.time()
            if 'message' in commit_trade[0]:
                logging.error('Error completing trading: {}'.format(commit_trade[0]['message']))
                return

            #make second trade
            logging.info('Step 2')
            trade = item[0][1]['best_trades'][1]
            logging.debug('Trade info: {}'.format(trade))
            if 'message' in commit_trade[0]:
                logging.error('Error completing trading: {}'.format(commit_trade[0]['message']))
                return  

            #make final trade
            logging.info('Step 3')
            trade = item[0][1]['best_trades'][2]
            logging.debug('Trade info: {}'.format(trade))
            if 'message' in commit_trade[0]:
                logging.error('Error completing trading: {}'.format(commit_trade[0]['message']))
                return   

        elif item[0][1]['best_case'] == 2:       
            #case 2: btc -> eth -> usd -> btc
            #get balance
            for x in comm.balances():
                if x['type'] == config.wallet_type and x['currency'] == config.currency_pref:
                    balance = x['amount']
                    logging.info('Current Balance: {} {}'.format(config.currency_pref, balance))          

            #first trade
            logging.info('Step 1')
            trade = item[0][1]['best_trades'][0]
            logging.debug('Trade info: {}'.format(trade))
            commit_trade = self.perform_trade(trade,False), time.time()
            if 'message' in commit_trade[0]:
                logging.error('Error completing trading: {}'.format(commit_trade[0]['message']))
                return

            #second trade
            logging.info('Step 2')
            trade = item[0][1]['best_trades'][1]
            logging.debug('Trade info: {}'.format(trade))
            commit_trade = self.perform_trade(trade,False), time.time()
            if 'message' in commit_trade[0]:
                logging.error('Error completing trading: {}'.format(commit_trade[0]['message']))
                return

            #third trade
            logging.info('step 3') 
            trade = item[0][1]['best_trades'][2]
            logging.debug('Trade info: {} Order type: {} Market: {}'.format(trade, config.order_type, config.market))
            commit_trade = self.perform_trade(trade,False), time.time()
            if 'message' in commit_trade[0]:
                logging.error('Error completing trading: {}'.format(commit_trade[0]['message']))
                return     

        for x in comm.balances():
                if x['type'] == config.wallet_type and x['currency'] == config.currency_pref:
                    balance = float(x['amount'])
                    TotalProfit = balance-StartBalance
                    logging.info('New Balance: {} {}'.format(config.currency_pref, balance))    
                    logging.info('Total profit: {} {}'.format(config.currency_pref, TotalProfit))

        if config.stop_bot_loss < 0: #incase user makes stop loss as negative number
            if TotalProfit <= config.stop_bot_loss:
                logging.error('Traded at loss. Terminating program.')
                os.system("pause")
                sys.exit()
        elif TotalProfit <= config.stop_bot_loss * -1:
            logging.error('Traded at loss. Terminating program.')
            os.system("pause")
            sys.exit()

    def recur(self, query_order, time_now):
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

    def verify(self, trans_str, time_now):
        while time.time() - time_now < ORDER_EXPIRATION_TIME:
            trans = eval(trans_str)
            if trans['status'] == 'ok':
                break
        return trans                    

    def perform_trade(self, trade, show_balance):
        query_order = comm.place_order(trade['amount'], trade['rate'], trade['type'], config.order_type, trade['pair'], config.market)
        return query_order 
       


