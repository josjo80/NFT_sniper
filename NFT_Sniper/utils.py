import json
import requests
import math
import numpy as np
import pickle 

from PIL import Image
from io import BytesIO
from functools import reduce

# Useful Lambas
gwei_to_eth = lambda gwei:  int(gwei) / 1e9
wei_to_eth = lambda wei:  int(wei) / 1e18
remove = lambda s, rm: s.translate({ord(i): None for i in rm}) # string removal
reduce_df = lambda dfs: reduce(lambda df1, df2: df1.merge(df2, how='outer'), dfs)
get = lambda url: requests.request("GET", url)
jtext = lambda url: json.loads(requests.request("GET", url).text)
maybe_unlist = lambda x: x[0] if len(x) == 1 else x
# keys_to_global_nms = lambda d: [globals().update(k, v) for k, v in d.items()]

def dict_append_all(d1, d2):
    assert sorted(list(d1)) == sorted(list(d2)) # keys MUST match
    assert isinstance(list(d1.values())[0], list)
    assert isinstance(list(d2.values())[0], list)
    d3 = {}
    for k, v1 in d1.items():
        v2 = d2[k]
        d3[k] = v1
        d3[k].extend(v2)
    del d1, d2
    return d3

# Creates an empty dict with the specified type as a default value
def typedict(keys=None, dtype=int):
    d = dict.fromkeys(keys)
    obj = {
        int: 0, float: 0.0,
        dict: {}, None: None,
        list: [], tuple: ()
    }[dtype]
    return {k: obj for k in d.keys()}

def logical2idx(x):
    x = np.asarray(x)
    return np.arange(len(x))[x]

def download_img(url):
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    return np.array(img)

def lengths(x):
    def maybe_len(e):
        if type(e) == list:
            return len(e)
        else:
            return 1
    if type(x) is not list: return [1]
    if len(x) == 1: return [1]
    return(list(map(maybe_len, x)))

def inorder(x, asc=True):
    i = 1
    x[len(x)] = -math.inf
    if asc:
        while x[i-1] <= x[i]: i += 1
    else:
        while x[i-1] >= x[i]: i += 1
    del x[len(x)-1]
    return True if i == len(x) else False

def is_numpy(x):
    return x.__class__ in [
        np.ndarray,
        np.rec.recarray,
        np.char.chararray,
        np.ma.masked_array
    ]

def is_scalar(x):
    if is_numpy(x):
        return x.ndim == 0
    if isinstance(x, str) or type(x) == bytes:
        return True
    if hasattr(x, "__len__"):
        return len(x) == 1
    try:
        x = iter(x)
    except:
        return True
    return np.asarray(x).ndim == 0

def unpickle(fp):
    with open(fp, 'rb') as f:
        x = pickle.load(f)
    return x

def jload(fp):
    with open(fp, 'rb') as f:
        x = json.load(f)
    return x

def loadz(fp, key='arr_0'):
    x = np.load(fp, allow_pickle=True)
    if is_scalar(key):
        return x[key]
    return {k: v for k,v in x.items() if k in keys}

def dict_up(l):
    """Wrap up a list of dicts into one dict"""
    raise NotImplementedError

def flatten_traits(d):
    return np.concatenate([list(v.keys()) for v in d.values()])

def sigmoid2(z):
    """ this function implements the sigmoid function, and 
        expects a numpy array as argument
    """
    if not isinstance(z, np.ndarray):
        z = np.asarray(z)    
    sigmoid = 1.0/(1.0 + np.exp(-z))
    return sigmoid 

def sigmoid(z):
    return 1/(1 + np.exp(-z))

def negate(x):
    return ~np.asarray(x).astype(bool)
