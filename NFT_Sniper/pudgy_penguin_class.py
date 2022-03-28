from __init__ import *


class PudgyPenguin:
    def __init__(self, 
                 tokenID, 
                 events=None, 
                 one_hot_features=None, 
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

    def set_sale_data(self):
        if self.events: return True
        events_series = load_pudgy_txns(self.tokenID)
        events_dict = invert_list_of_dict(events_series)
        self.events = pd.DataFrame(events_dict) # sets a pandas DataFrame

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


class PudgyEvent:
    def __init__(self, tokenID, sale_data):
        self.tokenID = tokenID
        self.penguin_object = PudgyPenguin(tokenID)
        self.sale_data = sale_data



if False:
    pp=PudgyPenguin(888)