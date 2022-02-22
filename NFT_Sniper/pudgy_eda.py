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

# INPUT:  ETH_PRICE, ONEHOT_TRAITS, IMAGE_DATA (?)
# OUTPUT: NFT PRICE

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
