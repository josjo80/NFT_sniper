
import json
import time
import requests

# https://stackoverflow.com/questions/66186408/python-how-to-get-ethereum-transactions
ETHERSCAN_API_KEY = "QXN3NDNXICBFTB1TEHZVZB6EYSXBZMUIP9"
CONTRACT_ADDRESS  = "0xbd3531da5cf5857e7cfaa92426877b022e612cf8"
GENESIS_TIMESTAMP = "2021-07-22"


def get_last_block():
    return int(json.loads(requests.get(
        "https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={}&closest=before&apikey={}".format(
            round(time.time()), ETHERSCAN_API_KEY)
    ).text)["result"])

def get_last_txs(n_blocks=10000):
    return json.loads(requests.get(
        "https://api.etherscan.io/api?module=account&action=txlist&address={}&startblock={}&sort=asc&apikey={}".format(
            CONTRACT_ADDRESS, get_last_block() - n_blocks, ETHERSCAN_API_KEY)
    ).text)["result"]

# Get a list of 'Internal' Transactions by Address
def get_internal_txs():
    return json.loads(requests.get(
        "https://api.etherscan.io/api?module=account&action=txlistinternal&address={}&startblock=0&endblock={}&sort=asc&apikey={}".format(
            CONTRACT_ADDRESS, get_last_block(), ETHERSCAN_API_KEY)
    ).text)['result']

# Get a list of "ERC721 - Token Transfer Events" by Address
    return json.loads(requests.get(
        "https://api.etherscan.io/api?module=account&action=tokennfttx&address={}&startblock=0&endblock={}&sort=asc&apikey={}".format(
            CONTRACT_ADDRESS, get_last_block(), ETHERSCAN_API_KEY)
    ).text)['result']

# Get a list of 'Normal' Transactions By Address, up to 10000
def get_all_txs():
    response = requests.get(
        "https://api.etherscan.io/api?module=account&action=txlist&address={}&startblock=0&endblock=99999999&sort=asc&apikey={}".format(
            CONTRACT_ADDRESS, ETHERSCAN_API_KEY))
    return json.loads(response.text)['result']

# (To get paginated results use page=<page number> and offset=<max records to return>)d
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

# Historical price (NOTE: ETHERSCAN PRO API REQUIRED)
def eth_price_at(date):
    """ Format: e.g. 2019-02-28 (yyyy-mm-dd)"""
    return json.loads(requests.get( # 2019-02-01, 2019-02-28
        "https://api.etherscan.io/api?module=stats&action=ethdailyprice&startdate={}&enddate={}&sort=asc&apikey={}".format(
            date, date, ETHERSCAN_API_KEY)
    ).text)['result']

ptx = get_paginated_txs(page=1, offset=10000)
atx = get_all_txs() # up to last 10000

pdf = pd.DataFrame(ptx)
adf = pd.DataFrame(txs)

"""
# We want:
TIMESTAMP (of txn/sale for time-series modeling)
ETH_PRICE (at time of txn [how bear/bull mkt affects pricing])
VALUE_ETH (amount sold for in Ether)
GAS_USED  (amount of gas used for txn)
"""