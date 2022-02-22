import json
import requests

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