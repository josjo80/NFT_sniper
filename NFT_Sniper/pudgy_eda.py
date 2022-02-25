import json
import requests
import pandas as pd
import numpy as np

from PIL import Image
from io import BytesIO

def logical2idx(x):
    x = np.asarray(x)
    return np.arange(len(x))[x]

def dict_up(l):
    """Wrap up a list of dicts into one dict"""
    raise NotImplementedError

def flatten_traits(d):
    return np.concatenate([list(v.keys()) for v in d.values()])

def encode_traits(t, dtype='int32'):
    x = np.array(list(map(lambda x: TRAIT2IDX[x['value'].lower()], t)))
    y = np.zeros(N_TRAITS, dtype=dtype)
    for i in x:
        y[i] = 1
    return y

def decode_traits(t):
    i = logical2idx(t.astype(bool))
    return TRAITS_LIST[i]

x = json.load(open('./data/pudgypenguins_data', 'r'))
md = x['pudgypenguins']['project_metadata']['collection']
sts = md['stats']
nfts = x['pudgypenguins']['nfts']
a = asset_link = md['image_url']
all_traits = md['traits']

TRAITS = set(sorted(flatten_traits(all_traits)))
TRAITS_LIST = np.asarray(list(TRAITS))
N_TRAITS = len(TRAITS)
TRAIT_SUPERCLASSES = set(all_traits)
TRAIT2IDX = dict(zip(TRAITS, range(N_TRAITS)))
IDX2TRAIT = dict(zip(range(N_TRAITS), TRAITS))

#preallocate
X = np.zeros((len(nfts), N_TRAITS))
for i, (nm, nft) in enumerate(nfts.items()):
    X[i] = encode_traits(nft['attributes'])

# save one hot vector
with open('./data/pudgyonehot.npz', 'wb') as f:
    np.savez(f, X) # penguin indexed by range(0, 8887)

#########################################################################################
# EXPERIMENTING...
#########################################################################################

path = './data/pudgy-txs'
files = list(map(lambda x: os.path.join(path, x), os.listdir(path)))
dfs = list(map(lambda x: pd.read_csv(x), files))

from functools import reduce
reduce_df = lambda dfs: reduce(lambda df1, df2: df1.merge(df2, how='outer'), dfs)

df = reduce_df(dfs)
hashes = df['Txhash']
txs_by_hash = []
for h in hashes:
    tx = get_tx_by_hash(h)
    txs_by_hash.append(tx)
    print(tx)
    break

ptxs = []
for i in range(10):
    ptx = get_paginated_txs(page=i, offset=5000)
    ptxs.append(ptx)
    print("-----------------")
    print(i)
    print("-----------------")

d0 = pd.DataFrame(ptxs[0]) # first 10000
d1 = pd.DataFrame(ptxs[1]) # 0:100
d2 = pd.DataFrame(ptxs[2]) # 100:200
d3 = pd.DataFrame(ptxs[3]) # 200:300
d4 = pd.DataFrame(ptxs[4]) # 300:400

a = d0.iloc[200:300].reset_index().drop(columns='index')
b = d3.reset_index().drop(columns='index')
print(all(a['hash']==b['hash']))

for 

ordered = lambda x: inorder(x['timeStamp'].astype(int))

import math
def inorder(x, asc=True):
    i = 1
    x[len(x)] = -math.inf
    if asc:
        while x[i-1] <= x[i]: i += 1
    else:
        while x[i-1] >= x[i]: i += 1
    del x[len(x)-1]
    return True if i == len(x) else False

# INPUT:  CURRENT_ETH_PRICE, ONEHOT_TRAITS, LIST_PRICE
# OUTPUT: EXPECTED_SALE_PRICE

# NOTE: Should we use hierarchical labels for traits? - are they standardized across projects?
tt = trait_tally = {}
for k,v in all_traits.items():
    trait_tally[k] = sorted(list(v.keys()))

def data_generator(nfts):
    for nm, nft in nfts.items():
        im = download_img(nft['image'])
        tv = decode_traits(traits_vec)
        ts = encode_traits(nft['attributes'])
        yield (nm, im, tv, ts)

for x in data_generator(nfts):
    print(x)

print("Done!")

df = pd.DataFrame.from_dict(nfts, orient='index')

# TODO:
# We're gonna need historical data...
# Pull all sales history: API from OpenSea ?!
# Item: Pudgy Penguin #6655
# Traits: One Hot vector [0, 1, 0, 1,..., 0] (len N_TRAITS)
# Sale Price: 1.08 ETH (2986.54 USD)
# Timestamp: 10:31:12-02-19-2022 (e.g.)
# some way to construct train-val splits. -> 


#ETHERSCAN PUDGYPENGUIN CONTRACT
# https://etherscan.io/address/0xbd3531da5cf5857e7cfaa92426877b022e612cf8

#ETHERSCAN PUDGYPENGUIN TOKEN
# https://etherscan.io/token/0xbd3531da5cf5857e7cfaa92426877b022e612cf8