# public market information
# currently using cryptowatch because the GDAX api gives wrong price ????
# options: Coinbase, Bitfinex, Cryptowatch
market = 'Coinbase'

market_expiration_time = 2 # how long to wait for orders to fill before cancel
market_reset_time = 45 # if bot cannot access market, it will wait to reset
order_type = 'market' # options: market, limit

# currency to start triangles with
# also used for displaying results
currency_pref = 'eur' 

currency_pairs = {
	'all':['btceur', 'ltcbtc', 'ltceur', 'ethbtc', 'etheur']
	}

# amount of currency to validate
# uses preferred currency
min_amount = 50 # min amount of bitcoin to validate
max_amount = 500 # max amount of bitcoin to validate
increment = 50

# loop check to avoid block
refresh_rate = 3
symbols = ['all']

# desired minimum profit in percentage (0.01 = 1%)
min_profit = 0.0001

# terminates the program if the bot loses this amount from starting balance (because of delays or incorrect values); uses the preferred currency
stop_bot_loss = 0.005

# transaction fee; standard taker fee = 0.3% (gdax)
fee = 0.003
slippage = 1

# used for private account info
# options: Coinbase_Trader, Traderbot_Finex
observers = [
'Coinbase_Trader'
]

demo_mode = False

# Key info
ACCESS_KEY = ''
SECRET_KEY = ''
PASSPHRASE = ''


