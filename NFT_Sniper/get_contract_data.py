
import json
import time
import requests

# https://stackoverflow.com/questions/66186408/python-how-to-get-ethereum-transactions
ETHERSCAN_API_KEY = "QXN3NDNXICBFTB1TEHZVZB6EYSXBZMUIP9"
CONTRACT_ADDRESS  = "0xbd3531da5cf5857e7cfaa92426877b022e612cf8"
GENESIS_TIMESTAMP = "2021-07-22"
GENESIS_BLOCK = 12876278

# https://etherscan.io/tx/0x5de14778174290ec856c6f3bf0aff822a3e91a3c32749beca311bd109772dbe3
def genesis_block():
    return GENESIS_BLOCK # deployer contract 

def get_last_block():
    return int(json.loads(requests.get(
        "https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={}&closest=before&apikey={}".format(
            round(time.time()), ETHERSCAN_API_KEY)
    ).text)["result"])

def get_last_txs(since=2):
    return json.loads(requests.get(
        "https://api.etherscan.io/api?module=account&action=txlist&address={}&startblock={}&sort=asc&apikey={}".format(
            CONTRACT_ADDRESS, get_last_block() - since, ETHERSCAN_API_KEY)
    ).text)["result"]

# Get a list of 'Internal' Transactions by Address
def get_internal_txs():
    return json.loads(requests.get(
        "https://api.etherscan.io/api?module=account&action=txlistinternal&address={}&startblock=0&endblock={}&sort=asc&apikey={}".format(
            CONTRACT_ADDRESS, get_last_block(), ETHERSCAN_API_KEY)
    ).text)['result']

# Get a list of "ERC721 - Token Transfer Events" by Address
def get_transfer_txs(end_block=999999999):
    return json.loads(requests.get(
        "https://api.etherscan.io/api?module=account&action=tokennfttx&address={}&startblock=0&endblock=999999999&sort=asc&apikey={}".format(
            CONTRACT_ADDRESS, ETHERSCAN_API_KEY)
    ).text)['result']

# Get a list of 'Normal' Transactions By Address, up to 10000
def get_all_txs():
    response = requests.get(
        "https://api.etherscan.io/api?module=account&action=txlist&address={}&startblock=0&endblock=99999999&sort=asc&apikey={}".format(
            CONTRACT_ADDRESS, ETHERSCAN_API_KEY))
    return json.loads(response.text)['result']

# Get a list of 'Normal' Transactions By Address, up to 10000
def get_tx_window(start_block, end_block):
    response = requests.get(
        "https://api.etherscan.io/api?module=account&action=txlist&address={}&startblock={}&endblock={}&sort=asc&apikey={}".format(
            CONTRACT_ADDRESS, start_block, end_block, ETHERSCAN_API_KEY)
        )
    return json.loads(response.text)['result']

# (To get paginated results use page=<page number> and offset=<max records to return>)d
# https://api.etherscan.io/api?module=account&action=tokennfttx&contractaddress=0x06012c8cf97bead5deae237070f9587f8e7a266d&address=0x6975be450864c02b4613023c2152ee0743572325&page=1&offset=100&sort=asc&apikey=YourApiKeyToken
def get_paginated_txs(page=1, offset=10):
    return json.loads(requests.get(
        "https://api.etherscan.io/api?module=account&action=txlist&address={}&startblock=0&endblock=99999999&page={}&offset={}&sort=asc&apikey={}".format(
            CONTRACT_ADDRESS, page, offset, ETHERSCAN_API_KEY)
    ).text)['result']

def last_eth_price():
    return json.loads(requests.get(
        "https://api.etherscan.io/api?module=stats&action=ethprice&apikey={}".format(
            ETHERSCAN_API_KEY)
    ).text)['result']

def get_tx_by_hash(tx_hash):
    return json.loads(requests.get(
        "https://api.etherscan.io/api?module=proxy&action=eth_getTransactionByHash&txhash={}&apikey={}".format(
            tx_hash, ETHERSCAN_API_KEY)
    ).text)['result']

# Historical price (NOTE: ETHERSCAN PRO API REQUIRED)
def eth_price_at(date):
    """ Format: e.g. 2019-02-28 (yyyy-mm-dd)"""
    return json.loads(requests.get( # 2019-02-01, 2019-02-28
        "https://api.etherscan.io/api?module=stats&action=ethdailyprice&startdate={}&enddate={}&sort=asc&apikey={}".format(
            date, date, ETHERSCAN_API_KEY)
    ).text)['result']


def get_block(block_no):
    return json.loads(requests.get(
        "https://api.etherscan.io/api?module=block&action=getblockreward&blockno={}&apikey={}".format(
        block_no, ETHERSCAN_API_KEY)
    ).text)['result']

if False:
    ptx1 = get_paginated_txs(page=1, offset=10000)
    ptx2 = get_paginated_txs(page=2, offset=10000)

    idx = logical2idx(adf['value'].astype(float) > 0)
    v = nonzero_values = adf.iloc[idx]

    atx = get_all_txs() # up to last 10000

    pdf = pd.DataFrame(ptx)
    adf = pd.DataFrame(atx)

"""
# We want:
TIMESTAMP (of txn/sale for time-series modeling)
ETH_PRICE (at time of txn [how bear/bull mkt affects pricing])
VALUE_ETH (amount sold for in Ether)
GAS_USED  (amount of gas used for txn)
"""

"""
Josh model:
CURRENT_ETH_PRICE
LAST_5_SALE_PRICES
LAST_5_ETH_PRICES
"""
