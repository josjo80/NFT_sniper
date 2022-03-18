from web3 import Web3
import json
import requests
import math
import time

CONTRACT_ADDRESS  = "0xbd3531da5cf5857e7cfaa92426877b022e612cf8" # PudgyPenguins
MAX_TOKENS = 8888
MORALIS_API_KEY = "xcJ9M9jsiM6mrllSMO3vYZTBzuz6ciat23RRRa4ESgVZ9p8AqW7kcD2TiHrmg5MB"

headers = {
    'x-api-key': MORALIS_API_KEY
}

gwei_to_eth = lambda gwei:  gwei / 1e9

# add blockchain connection info
chain = "eth"
eth = "https://speedy-nodes-nyc.moralis.io/a14ce974ce451fe65df03880/{}/mainnet".format(chain)
web3 = Web3(Web3.HTTPProvider(eth))
print(web3.isConnected())

addr = CONTRACT_ADDRESS
tokenAddr = web3.toChecksumAddress(addr)

tokenID = 0
nftTransfers = 'https://deep-index.moralis.io/api/v2/nft/{}/transfers?chain=eth&format=decimal'.format(tokenAddr)


# pudgyTransfers = {}
for tokenID in range(1501, MAX_TOKENS):
    url = 'https://deep-index.moralis.io/api/v2/nft/{}/{}/transfers?chain=eth&format=decimal'.format(
        tokenAddr, tokenID)
    response = requests.request("GET", url, headers=headers)
    
    resp = response.json()
    pudgyTransfers[tokenID] = resp['result']
    print("Got tokenID {}'s {} txns".format(tokenID, resp['total']))
    time.sleep(0.5)


with open("./data/pudgy_transactions_1911.json", 'w') as f:
    json.dump(pudgyTransfers, f)

# Process data
for tokenID, txns in pudgyTransfers.items():
    for txn in txns:
        eth_sale_price = gwei_to_eth(int(txn['value']))
    #TODO: WTF? Is this pointless?  
    # DO WE NEED OPENSEA TO GET LISTINGS TOO?!?! THIS SEEMS POINTLESS
    break

def calc_gwei_eth_price_at_sale(txn):
    ts = txn['block_timestamp']
    vl = txn['value']
    return get_eth_price_at_datetime_str(ts)['Close']
