import os
import pickle
import requests
import numpy as np
import pandas as pd
from pprint import pprint
from datetime import datetime
from dateutil.parser import parse

from .utils import loadz, jload, flatten_traits, reduce_df, logical2idx

# Set constants
ETHERSCAN_API_KEY = "QXN3NDNXICBFTB1TEHZVZB6EYSXBZMUIP9"
CONTRACT_ADDRESS  = "0xbd3531da5cf5857e7cfaa92426877b022e612cf8" # PudgyPenguins
MAX_TOKENS = 8888
IMAGE_DIR = "./images"

# GENESIS_DATE_STR = "Jul-22-2021 12:48:34 PM"
GENESIS_DATE_STR = "2021-07-22"
GENESIS_DATETIME = datetime(2021, 7, 22, 12, 48, 34)
GENESIS_TIMESTAMP = int(GENESIS_DATETIME.timestamp())
GENESIS_BLOCK = 12876278

# Load raw data
DATA_DIR = "./data"
PUDGY_RAW_DATA_PATH = os.path.join(DATA_DIR, "pudgypenguins_data_raw")
PUDGY_RAW_DATA = jload(PUDGY_RAW_DATA_PATH)
penguins = pd.DataFrame.from_dict(PUDGY_RAW_DATA['pudgypenguins']['nfts'], orient='index')

# Get sorted URLs list
PENGUIN_URLS = list(penguins['image'].values)
PENGUIN_URLS.sort(key=lambda x: int(x.split("/")[-1].split(".")[0]))

# One hot data
PUDGY_ONEHOT_PATH = os.path.join(DATA_DIR, "pudgy_onehot.npz")
POH = PUDGY_ONEHOT = loadz(PUDGY_ONEHOT_PATH)

# ADF = ALL_RARITY_DF = unpickle(os.path.join(DATA_DIR, "all_rarity_df.pickle"))
PUDGY_RARITY_PATH = os.path.join(DATA_DIR, "pudgypenguins2.xlsx")
RDF = PUDGY_RARITY_DF = pd.read_excel(PUDGY_RARITY_PATH)

ETH_HIST = pd.read_csv(os.path.join(DATA_DIR, "ETH-USD-History.csv"))

# Import class attributes and statistics
x = PUDGY_RAW_DATA
md = PUDGY_RAW_DATA['pudgypenguins']['project_metadata']['collection']
nfts = PUDGY_RAW_DATA['pudgypenguins']['nfts']
stats = md['stats']
asset_link = md['image_url']
all_traits = md['traits']

TRAITS = set(sorted(flatten_traits(all_traits)))
TRAITS_LIST = np.asarray(list(TRAITS))
N_TRAITS = len(TRAITS)
TRAIT_SUPERCLASSES = set(all_traits)
TRAIT2IDX = dict(zip(TRAITS, range(N_TRAITS)))
IDX2TRAIT = dict(zip(range(N_TRAITS), TRAITS))


def get_pudgy_images(penguin_urls=PENGUIN_URLS, start=0):
    penguin_urls = penguin_urls[start:]
    for url in penguin_urls:
        x  = requests.get(url)
        fp = os.path.join(IMAGE_DIR, "{}".format(url.split("/")[-1]))
        with open(fp, "wb") as f:
            f.write(x.content)
        print("Wrote penguin {}".format(url.split("/")[-1]))
        
def load_txn_data():
    path = os.path.join(DATA_DIR, 'pudgy-txs')
    files = list(
        map(
            lambda x: os.path.join(path, x), 
            os.listdir(path)
        )
    )
    dfs = list(map(lambda x: pd.read_csv(x), files))
    return reduce_df(dfs)

# Normalized ETH PRICE
def get_eth_price_at(unix_timestamp):
    unix_time = int(unix_timestamp)
    mint_date = datetime.utcfromtimestamp(unix_time).strftime('%Y-%m-%d %H:%M:%S')
    return ETH_HIST.iloc[logical2idx(ETH_HIST['Date'] == mint_date[:-9])[0]]

def str_datetime_to_unix(datetime_str):
    return int(parse(datetime_str).timestamp())

def get_eth_price_at_datetime_str(datetime_str, return_single_value=True):
    x = get_eth_price_at(str_datetime_to_unix(datetime_str))
    return x['Close'] if return_single_value else x

eth_to_usd = lambda eth, ds: float(eth) * get_eth_price_at_datetime_str(ds)

PUDGY_TXN_DF = load_txn_data()
ETH_MINT_PRICE = get_eth_price_at(GENESIS_TIMESTAMP)['Close']
GENESIS_PRICE_USD = ETH_MINT_PRICE

def load_pudgy_txn_df():
    with open("./data/pudgy_transactions.pickle", 'rb') as f:
        x = pickle.load(f)
    df = pd.DataFrame.from_dict(x, orient='index')
    return df

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

def load_pudgy_txn_dict():
    with open("./data/pudgy_transactions.pickle", 'rb') as f:
        x = pickle.load(f)
    return x

def load_pudgy_txns(tokenID):
    """
    Load pudgy transaction data by tokenID.
    Param:
        tokenID: Integer. Pudgy token index. (0,8887)
    
    Returns:
        Numpy array of chronological transactions and associated metadata
    """
    df = load_pudgy_txn_df()
    txn_series = df.iloc[int(tokenID)]
    idx = logical2idx(list(map(lambda x: x != None, txn_series.values)))
    txns = txn_series[idx].values
    return txns

# Convert list of dicts WITH SAME KEYS to single dict, using append
def invert_list_of_dict(list_of_dicts):
    x = list(map(lambda x: list(x.keys()), list_of_dicts))
    k1 = x[0]
    for keys in x:
        if keys != k1:
            raise ValueError("All keys must be identical accross dictionaries")
    out = {k: [] for k in k1}
    for d in list_of_dicts:
        for k,v in d.items():
            out[k].append(v)
    return out


EMBEDDING_DIM = 64
from .embeddings import get_pudgy_embeddings
PUDGY_EMBEDDING = get_pudgy_embeddings(POH, EMBEDDING_DIM)