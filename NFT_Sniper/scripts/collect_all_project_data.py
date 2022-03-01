import requests
import json
import argparse

import pandas as pd
from time import sleep
from collections import defaultdict
from utils import *


PROJECT_NAMES = ['pudgypenguins', 
'boredapeyachtclub', 'cryptopunks', 'mushrohms', 'world-of-women-nft']
DEFAULT_EXE = r"C:\Users\{}\Downloads\geckodriver-v0.30.0-win64\geckodriver.exe".format(
    'stgeorge')

parser = argparse.ArgumentParser(
    description='Collect data & metadata for a given NFT project')
parser.add_argument(
    '-n','--name', help='NFT Project Name', default='pudgypenguins')
parser.add_argument(
    '-g','--gecko_path', help='Path to `geckodriver.exe`', default=DEFAULT_EXE)
args = vars(parser.parse_args())

exe_path = args['gecko_path']
name = args['name']

nfts = {}
c = collection = typedict(['pudgypenguins'], dict)

url = "https://api.opensea.io/api/v1/collection/{}".format(name)
data = jtext(url)
primary_contracts = maybe_unlist(data['collection']['primary_asset_contracts'])
contract_address  = primary_contracts['address']

etherscan_addr = "https://etherscan.io/address/{}#readContract".format(contract_address)

# Pudgy Penguins URI Format
# https://ipfs.io/ipfs/QmWXJXRdExse2YHRY21Wvh4pjRxNRQcWVhcKw4DLVnqGqs/

max_nfts = 8888 + 1
base_uri = "https://ipfs.io/ipfs/QmWXJXRdExse2YHRY21Wvh4pjRxNRQcWVhcKw4DLVnqGqs/" 

collection[name]['project_metadata'] = data
collection[name]['base_uri'] = base_uri
collection[name]['nfts'] = {}

for i in range(start, end): # max_nfts
    if i % 100 == 0:
        print("Processing {} of {} requests...".format(i, max_nfts))
    if "ipfs" == base_uri[:4]: #base_uri.count('ipfs'): # if it's an ipfs link
        uri = base_uri.split("//")[1]
        # base_uri = "QmeSjSinHpPnmXmspMjwiXyN6zS4E9zccariGR3jxcaWtq"
        url = "https://ipfs.io/ipfs/{}/{}".format(uri, i)
        try:
            nft = jtext(url)
            nfts[str(i)] = nft
        except:
            print("Bad response... {}".format(i))
    else:
        try:
            nft = jtext(base_uri + str(i))
            nfts[nft['name']] = nft
        except:
            print("Bad response... {}".format(i))
            try:
                nft = jtext(base_uri + str(i) + '.json')
                nfts[nft['name']] = nft
            except:
                print("Bad response w/ .json... {}".format(i))

collection[name]['nfts'] = nfts


with open('./{}_data_raw'.format(name), 'w') as f:
    json.dump(collection, f)

# NOTE:
# https://stackoverflow.com/questions/68940662/download-images-from-ipfs
# https://pypi.org/project/ipfs-api/
# https://www.cnblogs.com/yoyo1216/p/13489699.html
