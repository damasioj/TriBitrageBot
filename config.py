# market information
# options: Coinbase, Bitfinex
market = 'Coinbase'

# secondary market sources
sec_markets = ['Cryptowatch']

market_expiration_time = 2 # how long to wait for orders to fill before cancel
market_reset_time = 45 # if bot cannot access market, it will wait to reset
order_type = 'market' # options: market, limit

# currency to start triangles with (for bitfinex you must use USD or crypto)
currency_pref = 'btc'

currency_pairs = {
	'gdax':['btceur', 'ltcbtc', 'ltceur', 'ethbtc', 'etheur'],
	'bitfinex':['btcusd', 'btceur', 'ltcusd', 'ltcbtc', 'ethusd', 'ethbtc', 'xrpusd', 'xrpbtc']
	}

# currency pairs to be used
symbols = 'gdax'

# amount of currency to validate
# uses preferred currency
min_amount = 0.0055
max_amount = 0.1
increment = 0.0165

# loop check to avoid block
refresh_rate = 2

# desired minimum profit in percentage (0.01 = 1%)
min_profit = 0.0001

# terminates the program if the bot loses this amount from starting balance (because of delays or incorrect values); uses the preferred currency
stop_bot_loss = 0.005

# transaction fee
# gdax : 0.3%
# bitfinex : 0.2%
fee = 0.003
slippage = 1

# used for connecting to authenticated services
# options: Coinbase_Trader, Traderbot_Finex
observers = [
'Coinbase_Trader'
]

demo_mode = False

# Key info
ACCESS_KEY = ''
SECRET_KEY = ''
PASSPHRASE = ''
