"""
This file can be used to easily modify which pairs are stored and displayed throughout the entire application

Supported Coinbase Symbols:
"BTC-USD", "ETH-USD", "LTC-USD", "BTC-EUR", "BCH-USD", "ETH-EUR",
"LTC-EUR", "ETH-BTC", "LTC-BTC", "BTC-GDP", "BCH-BTC", "BCH-EUR"


Supported Bitfinex Symbols:

"BTCUSD","LTCUSD","LTCBTC","ETHUSD","ETHBTC","ETCBTC","ETCUSD",
"RRTUSD","RRTBTC","ZECUSD","ZECBTC","XMRUSD","XMRBTC","DSHUSD",
"DSHBTC","BTCEUR","XRPUSD","XRPBTC","IOTUSD","IOTBTC","IOTETH",
"EOSUSD","EOSBTC","EOSETH","SANUSD","SANBTC","SANETH","OMGUSD",
"OMGBTC","OMGETH","BCHUSD","BCHBTC","BCHETH","NEOUSD","NEOBTC",
"NEOETH","ETPUSD","ETPBTC","ETPETH","QTMUSD","QTMBTC","QTMETH",
"AVTUSD","AVTBTC","AVTETH","EDOUSD","EDOBTC","EDOETH","BTGUSD",
"BTGBTC","DATUSD","DATBTC","DATETH","QSHUSD","QSHBTC","QSHETH",
"YYWUSD","YYWBTC","YYWETH","GNTUSD","GNTBTC","GNTETH","SNTUSD",
"SNTBTC","SNTETH","IOTEUR","BATUSD","BATBTC","BATETH","MNAUSD",
"MNABTC","MNAETH","FUNUSD","FUNBTC","FUNETH","ZRXUSD","ZRXBTC",
"ZRXETH","TNBUSD","TNBBTC","TNBETH","SPKUSD","SPKBTC","SPKETH",
"TRXUSD","TRXBTC","TRXETH","RCNUSD","RCNBTC","RCNETH","RLCUSD",
"RLCBTC","RLCETH","AIDUSD","AIDBTC","AIDETH","SNGUSD","SNGBTC",
"SNGETH","REPUSD","REPBTC","REPETH","ELFUSD","ELFBTC","ELFETH"
"""
pairIDs = {}

coinbasePairs = [
    'ETH-USD'
]

bitfinexPairs = [
    "BTCUSD"
]

#removes hyphen between currencies if the pair is coinbase format
def pairFormatter(pair):
    return pair if len(pair) == 6 else pair[:3] + pair[4:]

#returns the id of the pair in the database
def getPairID(pair):
    return pairIDs[pairFormatter(pair)]
