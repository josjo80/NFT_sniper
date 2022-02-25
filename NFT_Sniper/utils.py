import json
import requests
import math
import numpy as np

from PIL import Image
from io import BytesIO

# Useful Lambas
get = lambda url: requests.request("GET", url)
jtext = lambda url: json.loads(requests.request("GET", url).text)
maybe_unlist = lambda x: x[0] if len(x) == 1 else x
# keys_to_global_nms = lambda d: [globals()[k] = v for k, v in d.items()]

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