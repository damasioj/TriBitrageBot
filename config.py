# public market information
# currently using cryptowatch because the GDAX api gives wrong price ????
# options: Coinbase, Bitfinex, Cryptowatch
market = 'Cryptowatch'

market_expiration_time = 2 # how long to wait for orders to fill before cancel
market_reset_time = 45 # if bot cannot access market, it will wait to reset
order_type = 'market' # options: market, limit
currency_pref = 'btc' # the preferred currency to display balances and other info; btc, usd, eth

currency_pairs = {
	'all':['btceur', 'ltcbtc', 'ltceur', 'ethbtc', 'etheur']
	}

min_amount = 0.01 # min amount of bitcoin to validate
max_amount = 0.08 # max amount of bitcoin to validate
increment = 0.01

# loop check to avoid block
refresh_rate = 2
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
ACCESS_KEY = 'd95ba21d18528d081533b4e6c45662ae'
SECRET_KEY = 'Zsieqa+6O+NOdPbStGuSGM3DQM42/RyY9y4stmfz368GTyr4uvuFZ6adQ1jbwBm7kjzOYbEKRjc5mV3/xUY/xg=='
PASSPHRASE = 'sm48yq2yxe8'


