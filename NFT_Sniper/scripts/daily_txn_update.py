import os
import datetime
from dateutil.parser import parse

from web3 import Web3
import requests
import pickle

import time

def load_pudgy_txn_dict2(path='./data'):
    """
    Checks for most recent version with str datetime:
        format: YYYYMMDD-HHMMSS
    """
    files = os.listdir(path)
    cur = datetime.min
    for fp in files:
        date = os.path.split(fp)[-1].split('_')[-1]
        if date.split(".")[-1] == 'pickle':
            date = date.split(".")[0]
        try:
            dt_str = parse(date)
            if dt_str > cur:
                cur = dt_str
                filepath = os.path.join(path, fp)
        except:
            pass
    with open(filepath, 'rb') as f:
        x = pickle.load(f)
    return x

timestamp = lambda: time.strftime("%Y%m%d-%H%M%S")
gwei_to_eth = lambda gwei:  gwei / 1e9
wei_to_eth = lambda wei:  wei / 1e18

CONTRACT_ADDRESS  = "0xbd3531da5cf5857e7cfaa92426877b022e612cf8" # PudgyPenguins
MAX_TOKENS = 8888
MORALIS_API_KEY = "xcJ9M9jsiM6mrllSMO3vYZTBzuz6ciat23RRRa4ESgVZ9p8AqW7kcD2TiHrmg5MB"

headers = {
    'x-api-key': MORALIS_API_KEY
}

# add blockchain connection info
chain = "eth"
eth = "https://speedy-nodes-nyc.moralis.io/a14ce974ce451fe65df03880/{}/mainnet".format(chain)
web3 = Web3(Web3.HTTPProvider(eth))
print(web3.isConnected())

addr = CONTRACT_ADDRESS
tokenAddr = web3.toChecksumAddress(addr)

tokenID = 0
nftTransfers = 'https://deep-index.moralis.io/api/v2/nft/{}/transfers?chain=eth&format=decimal'.format(tokenAddr)


# Load existing txn dict/df
# LOAD MOST RECENT
pudgys = load_pudgy_txn_dict2()

skipped = []
for tokenID in list(pudgys):
    url = 'https://deep-index.moralis.io/api/v2/nft/{}/{}/transfers?chain=eth&format=decimal'.format(
        tokenAddr, tokenID)
    old_txns = pudgys[tokenID]
    try:
        response = requests.request("GET", url, headers=headers)
        resp = response.json()
        new_txns = resp['result']
    except:
        print("Error with tokenID {}".format(tokenID))
        skipped.append(tokenID)
        continue
    if len(new_txns) > len(old_txns):
        pudgys[tokenID] = new_txns
        print("Updating tokenID {} with {} new txn(s)".format(
            tokenID, len(new_txns) - len(old_txns)))
        assert len(pudgys[tokenID]) > len(old_txns)
    time.sleep(0.1)


completed_time = timestamp()

with open("./data/pudgy_transactions_{}.pickle".format(completed_time), 'wb') as f:
    pickle.dump(pudgys, f)

with open("./data/pudgy_transactions_skipped_{}.pickle".format(completed_time), 'wb') as f:
    pickle.dump(skipped, f)


