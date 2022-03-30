from __init__ import *
from copy import deepcopy
from pprint import pprint, pformat


def encode_pudgy_traits(t, dtype='int32'):
    x = np.array(list(map(lambda x: TRAIT2IDX[x['value'].lower()], t)))
    y = np.zeros(N_TRAITS, dtype=dtype)
    for i in x:
        y[i] = 1
    return y

def decode_pudgy_traits(t):
    return TRAITS_LIST[t.astype(bool)]

DROP_COLS = [
 'block_number',
 'block_timestamp',
 'block_hash',
 'transaction_hash',
 'transaction_index',
 'log_index',
 'value',
 'contract_type',
 'transaction_type',
 'token_address',
 'token_id',
 'from_address',
 'to_address',
 'amount',
 'verified',
 'operator'
]

class PudgyPenguin:
    def __init__(self, 
                 tokenID, 
                 events=None, 
                 one_hot_features=None, 
                 string_features=None,
                 one_hot_path=PUDGY_ONEHOT_PATH,
                 rarity_score=None, 
                 rarity_score_norm=None,
                 rarity_freq=None,
                 image_data=None,
                 current_floor_price_ETH=None,
                 current_floor_price_USD=None):

        self.tokenID = tokenID
        self.events = events # sales
        self.one_hot_path = one_hot_path
        self.one_hot_features = one_hot_features
        self.string_features = string_features
        self.rarity_score = rarity_score
        self.rairty_score_norm = rarity_score_norm
        self.rarity_freq = rarity_freq
        self.image_data = image_data
        self.current_floor_price_ETH = current_floor_price_ETH
        self.current_floor_price_USD = current_floor_price_USD

        self.mint_price = None
        self.market_cap = None
        self.thirty_day_avg_price = None
        self.seven_day_average_price = None
        self.one_day_average_price = None

        self.set_current_floor_price()
        self.set_image_data()
        self.set_one_hot_features()
        self.set_rarity_score()
        self.set_sale_data()

    def __str__(self):
        dct = deepcopy(self.__dict__)
        dct.pop('image_data')
        dct['one_hot_features']
        string = pformat(dct)
        return string

    def set_str_features(self):
        if not self.one_hot_features:
            self.set_one_hot_features()
        self.string_features = decode_pudgy_traits(self.one_hot_features)

    def set_sale_data(self):
        if self.events: return True
        events_series = load_pudgy_txns(self.tokenID)
        events_dict = invert_list_of_dict(events_series)
        events = pd.DataFrame(events_dict) 
        events.loc[:, "ETH_price_at_sale"] = events['block_timestamp'].apply(get_eth_price_at_datetime_str)
        events.loc[:, "sale_price_ETH"] = events['value'].apply(wei_to_eth)
        events.loc[:, "sale_price_USD"] = events['sale_price_ETH'] * events['ETH_price_at_sale']
        self.events = events

    def set_current_floor_price(self):
        self.current_floor_price_ETH = float(get_current_pudgy_floor_price())
        self.current_floor_price_USD = last_eth_price() * self.current_floor_price_ETH
 
    def set_image_data(self):
        if self.image_data: return True
        url = PENGUIN_URLS[self.tokenID]
        fp = os.path.join(
            IMAGE_DIR, 
            "{}".format(url.split("/")[-1])
        )
        self.image_data = np.array(PIL.Image.open(fp))

    def set_one_hot_features(self):
        if self.one_hot_features:
            return True
        self.one_hot_features = PUDGY_ONEHOT[self.tokenID]

    def set_rarity_score(self):
        if self.rarity_score:
            return True
        rare_series = PUDGY_RARITY_DF.iloc[self.tokenID]
        rarity_freq = np.asarray([   
            rare_series['Freq. (%).1'],
            rare_series['Freq. (%).2'],
            rare_series['Freq. (%).3'],
            rare_series['Freq. (%).4'],
            rare_series['Freq. (%).5']
        ])
        self.rarity_score = rare_series['Rarity score']
        self.rairty_score_norm = rare_series['Rarity score normed']
        self.rarity_freq = rarity_freq

    def return_all_data(self):
        raise NotImplementedError



class PudgyEvent:
    def __init__(self, tokenID, sale_data):
        self.tokenID = tokenID
        self.penguin_object = PudgyPenguin(tokenID)
        self.sale_data = sale_data



if False:
    penguins = {}
    for tokenID in range(10):
        penguins[tokenID]=PudgyPenguin(tokenID)
