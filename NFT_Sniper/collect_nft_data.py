# https://stackoverflow.com/questions/70306391/scraping-prices-from-opensea
import requests

def collect_nft_data(nft_address:str, collection_size:int) -> dict:
    """This will get the data on all the nfts in a collection, so long as you input the correct 
    nft_address and collection size, and return it in a dictionary""" 

    #create a dictionary to store your data for each asset in the collection
    asset_data = dict()

    #call the api to collect data on each asset in the collection the token_id usually corresponds to a number i.e. there are 10000 assets in a collection and you want the first asset, the tokenID 
    #is usually 1. So in our loop, i will be the tokenID of each asset
    for i in range(1, collection_size+1):
        url = "https://api.opensea.io/api/v1/assets?token_ids={}&asset_contract_address={}&order_direction=desc&offset=0&limit=20".format(
            i, nft_address)

        headers = {"Accept": "application/json"}

        response = requests.request("GET", url, headers=headers)

        asset_data['token_' + str(i)] = response.text

    return asset_data

address="0xbd3531da5cf5857e7cfaa92426877b022e612cf8"
num_assets=8
data = collect_nft_data(address, num_assets)
# https://github.com/dcts/opensea-scraper



# https://gist.github.com/dcts/a1b689b88e61fe350a446a5799209c9b
import cloudscraper
import json

def filter_typename(dict):
  return dict["__typename"] == "AssetQuantityType"

def filter_quantityInEth_exists(dict):
  if "quantityInEth" in dict:
    return True
  else:
    return False

def get_floor_price_in_eth(dict):
  return float(dict["quantity"]) / 1000000000000000000

def get_floor_prices(slug):
  scraper = cloudscraper.create_scraper(
    browser={
      'browser': 'chrome',
      'platform': 'android',
      'desktop': False
    }
  )
  url = "https://opensea.io/collection/{}?search[sortAscending]=true&search[sortBy]=PRICE&search[toggles][0]=BUY_NOW".format(slug);
  html = scraper.get(url).text
  json_string = html.split("</script>",2)[0].split("window.__wired__=",2)[1]
  data = json.loads(json_string)
  data_values = data["records"].values() # get all values type...
  data_list = [*data_values] # convert to list =~ array in js
  data_list = list(filter(filter_typename, data_list))
  data_list = list(filter(filter_quantityInEth_exists, data_list))
  data_list = list(map(get_floor_price_in_eth, data_list))
  return data_list


# scraping floor prices from opensea
print("RUNNING FOR cool-cats-nft")
print(get_floor_prices("cool-cats-nft"))
print("RUNNING FOR treeverse")
print(get_floor_prices("treeverse"))




# http://adilmoujahid.com/posts/2021/06/data-mining-meebits-nfts-python-opensea/