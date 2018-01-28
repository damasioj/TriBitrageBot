# public market information
# currently using cryptowatch because the GDAX api gives wrong price ????
# options: Coinbase, Bitfinex, Cryptowatch
market = 'Bitfinex'

market_expiration_time = 2 # how long to wait for orders to fill before cancel
market_reset_time = 45 # if bot cannot access market, it will wait to reset
order_type = 'market' # options: market, limit

# currency to start triangles with (for bitfinex you must use USD or crypto)
# also used for displaying results
currency_pref = 'usd'

currency_pairs = {
	'gdax':['btceur', 'ltcbtc', 'ltceur', 'ethbtc', 'etheur'],
        'bitfinex':['btcusd', 'btceur', 'ltcusd', 'ltcbtc', 'ethusd', 'ethbtc', 'xrpusd', 'xrpbtc']
	}

# currency pairs to be used
symbols = 'bitfinex'

# amount of currency to validate
# uses preferred currency
min_amount = 20 # min amount of bitcoin to validate
max_amount = 200 # max amount of bitcoin to validate
increment = 10

# loop check to avoid block
refresh_rate = 8


# desired minimum profit in percentage (0.01 = 1%)
min_profit = 0.0001

# terminates the program if the bot loses this amount from starting balance (because of delays or incorrect values); uses the preferred currency
stop_bot_loss = 0.005

# transaction fee; standard taker fee = 0.25% (gdax)
fee = 0.0025
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


