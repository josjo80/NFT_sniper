# https://github.com/adilmoujahid/data-mining-nfts/blob/main/data-mining-meebits-nfts.ipynb



import pandas as pd

import pymongo
from pymongo import MongoClient
import requests 

import matplotlib
import matplotlib.pyplot as plt

plt.style.use('ggplot')

#Setting up a MongoDB Connection

client = MongoClient()
db = client.meebitsDB
meebits_collection = db.meebitsCollection
sales_collection = db.salesCollection



def parse_meebit_data(meebit_dict):
    
    meebit_id = meebit_dict['token_id']
    
    try:
        creator_username = meebit_dict['creator']['user']['username']
    except:
        creator_username = None
    try:
        creator_address = meebit_dict['creator']['address']
    except:
        creator_address = None
    
    try:
        owner_username = meebit_dict['owner']['user']['username']
    except:
        owner_username = None
    
    owner_address = meebit_dict['owner']['address']
    
    traits = meebit_dict['traits']
    num_sales = int(meebit_dict['num_sales'])
        
    result = {'meebit_id': meebit_id,
              'creator_username': creator_username,
              'creator_address': creator_address,
              'owner_username': owner_username,
              'owner_address': owner_address,
              'traits': traits,
              'num_sales': num_sales}
    
    return result


def parse_sale_data(sale_dict):
    
    is_bundle = False

    if sale_dict['asset'] != None:
        meebit_id = sale_dict['asset']['token_id']
    elif sale_dict['asset_bundle'] != None:
        meebit_id = [asset['token_id'] for asset in sale_dict['asset_bundle']['assets']]
        is_bundle = True
    
    
    seller_address = sale_dict['seller']['address']
    buyer_address = sale_dict['winner_account']['address']
    
    try:
        seller_username = sale_dict['seller']['user']['username']
    except:
        seller_username = None    
    try:
        buyer_username = sale_dict['winner_account']['user']['username']
    except:
        buyer_username = None
    
    timestamp = sale_dict['transaction']['timestamp']
    total_price = float(sale_dict['total_price'])
    payment_token = sale_dict['payment_token']['symbol']
    usd_price = float(sale_dict['payment_token']['usd_price'])
    transaction_hash = sale_dict['transaction']['transaction_hash']
    

    result = {'is_bundle': is_bundle,
              'meebit_id': meebit_id,
              'seller_address': seller_address,
              'buyer_address': buyer_address,
              'buyer_username': buyer_username,
              'seller_username':seller_username,
              'timestamp': timestamp,
              'total_price': total_price, 
              'payment_token': payment_token,
              'usd_price': usd_price,
              'transaction_hash': transaction_hash}
    
    return result



# COLLECT ASSET DATA
"""
The source code below collects assets data about the 20,000 Meebits. 
The API has a limit of 50 items per call, and therefore we need to 
create a loop with 400 iterations to collect all Meebits data.
"""

url = "https://api.opensea.io/api/v1/assets"

for i in range(0, 400):
    querystring = {"token_ids":list(range((i*50)+1, (i*50)+51)),
                   "asset_contract_address":"0x7Bd29408f11D2bFC23c34f18275bBf23bB716Bc7",
                   "order_direction":"desc",
                   "offset":"0",
                   "limit":"50"}
    response = requests.request("GET", url, params=querystring)
    
    print(i, end=" ")
    if response.status_code != 200:
        print('error')
        break
    
    #Getting meebits data
    meebits = response.json()['assets']
    #Parsing meebits data
    parsed_meebits = [parse_meebit_data(meebit) for meebit in meebits]
    #storing parsed meebits data into MongoDB
    meebits_collection.insert_many(parsed_meebits)




"""
After collecting Meebits data, we need to confirm the total numbers of Meebits sales. 
To do this, from a Mongo shell, we execute the following command.

{mongo}
use meebitsDB

db.getCollection('meebitsCollection').aggregate([ { 
    $group: { 
        _id: null, 
        total: { 
            $sum: "$num_sales" 
        } 
    } 
} ] )

At the time of writing, we have 4,644 sales.
"""
    


# COLLECT SALES DATA
"""
The source code below collects all sale transactions data. 
The API has a limit of 50 items per call, and therefore we 
need to create a loop to collect all sale transactions data.
"""
url = "https://api.opensea.io/api/v1/events"

for i in range(0, 100):

    querystring = {"asset_contract_address":"0x7bd29408f11d2bfc23c34f18275bbf23bb716bc7",
                   "event_type":"successful",
                   "only_opensea":"true",
                   "offset":i*50,
                   "limit":"50"}

    headers = {"Accept": "application/json"}

    response = requests.request("GET", url, headers=headers, params=querystring)

    
    print(i, end=" ")
    if response.status_code != 200:
        print('error')
        break
    
    #Getting meebits sales data
    meebit_sales = response.json()['asset_events']

    if meebit_sales == []:
        break
    
    #Parsing meebits sales data
    parsed_meebit_sales = [parse_sale_data(sale) for sale in meebit_sales]
    #storing parsed meebits data into MongoDB
    sales_collection.insert_many(parsed_meebit_sales)


# We start by reading both the assets data and the transactions data into 2 Pandas DataFrames.

meebits = meebits_collection.find()
meebits_df = pd.DataFrame(meebits)

meebit_sales = sales_collection.find()
meebit_sales_df = pd.DataFrame(meebit_sales)


print("The database has information about %d Meebits." % len(meebits_df))
print("The database has information about %d Meebits sale transactions." % len(meebit_sales_df))


# Getting Top 10 Meebits Creators
creators = []
for creator_address in meebits_df['creator_address'].value_counts().index[:10]:
    creator_data = {}
    creator_data['creator_address'] = creator_address
    creator_data['creator_username'] = meebits_df[meebits_df['creator_address'] == creator_address]['creator_username'].iloc[0]
    creator_data['number_meebits'] = len(meebits_df[meebits_df['creator_address'] == creator_address])
    creators.append(creator_data)

pd.DataFrame(creators)



# Getting Stats about Bundle/Single Sales and Types of Payment
meebit_sales_df['is_bundle'].value_counts()
meebit_sales_df[meebit_sales_df['is_bundle'] == False]['payment_token'].value_counts()


# Filering Sale Transactions and Adding New Features
# To make the analysis easier, we will only focus on single sales done in ETH or WETH.
meebit_sales_df = meebit_sales_df[(meebit_sales_df['payment_token'] != 'USDC') & (meebit_sales_df['is_bundle'] == False)].copy()



# Next, we do some data cleaning and we add a new feature

# Parsing dates
meebit_sales_df['timestamp'] = pd.to_datetime(meebit_sales_df['timestamp'])
# Converting sales price from WEI to ETH
meebit_sales_df['total_price'] = meebit_sales_df['total_price']/10.**18
# Calculating the sale prices in USD
meebit_sales_df['total_price_usd'] = meebit_sales_df['total_price'] * meebit_sales_df['usd_price']



## Meebits Sales Timelines

# Total Number of Sales per Day
data = meebit_sales_df[['timestamp', 'total_price']].resample('D', on='timestamp').count()['total_price']
ax = data.plot.bar(figsize=(18, 6))

ax.set_alpha(0.8)
ax.set_title("Number of Meebits Sales per Day", fontsize=18)
ax.set_ylabel("Number of Meebits Sales", fontsize=18)

#https://github.com/pandas-dev/pandas/issues/1918
plt.gca().xaxis.set_major_formatter(plt.FixedFormatter(data.index.to_series().dt.strftime("%d %b %Y")))

#https://robertmitchellv.com/blog-bar-chart-annotations-pandas-mpl.html
for i in ax.patches:
    # get_x pulls left or right; get_height pushes up or down
    ax.text(i.get_x(), i.get_height()+40, \
            str(round((i.get_height()), 2)), fontsize=11, color='dimgrey',
                rotation=45)


# Total Sales per Day in ETH
data = meebit_sales_df[['timestamp', 'total_price']].resample('D', on='timestamp').sum()['total_price']
ax = data.plot(figsize=(18,6), color="red", linewidth=1, marker='o', markerfacecolor='grey', markeredgewidth=0)

ax.set_alpha(0.8)
ax.set_title("Timeline of Total Meebit Sales in ETH", fontsize=18)
ax.set_ylabel("Sales in ETH", fontsize=18);

dates = list(data.index)
values = list(data.values)

for i, j in zip(dates, values):
    ax.annotate(s="{:.0f}".format(j), xy=(i, j+200), rotation=45)



# Total Sales per day in USD
data = meebit_sales_df[['timestamp', 'total_price_usd']].resample('D', on='timestamp').sum()['total_price_usd']
ax = data.plot(figsize=(18,6), color="red", linewidth=1, marker='o', markerfacecolor='grey', markeredgewidth=0)

ax.set_alpha(0.8)
ax.set_title("Timeline of Total Meebit Sales in Million USD", fontsize=18)
ax.set_ylabel("Sales in Million USD", fontsize=18);

dates = list(data.index)
values = list(data.values)

for i, j in zip(dates, values):
    ax.annotate(s="{:.2f}".format(j/10.**6), xy=(i, j), rotation=45)



# Average Meebit Price per Day in ETH
data = meebit_sales_df[['timestamp', 'total_price']].resample('D', on='timestamp').mean()['total_price']
ax = data.plot(figsize=(18,6), color="green", linewidth=1, marker='o', markerfacecolor='grey', markeredgewidth=0)

ax.set_alpha(0.8)
ax.set_title("Timeline of Average Meebit Price in ETH", fontsize=18)
ax.set_ylabel("Average Price in ETH", fontsize=18);
#ax.annotate(s='sdsdsds', xy=(1, 1))

dates = list(data.index)
values = list(data.values)

for i, j in zip(dates, values):
    ax.annotate(s="{:.2f}".format(j), xy=(i, j+.2), rotation=45)



# Floor Meebit Price per Day in ETH
data = meebit_sales_df[['timestamp', 'total_price']].resample('D', on='timestamp').min()['total_price']
ax = data.plot(figsize=(18,6), color="orange", linewidth=1, marker='o', markerfacecolor='grey', markeredgewidth=0)

ax.set_alpha(0.8)
ax.set_title("Timeline of Floor Meebit Price in ETH", fontsize=18)
ax.set_ylabel("Floor Price in ETH", fontsize=18);

dates = list(data.index)
values = list(data.values)

for d, v in zip(dates, values):
    ax.annotate(s="{:.2f}".format(v), xy=(d, v), rotation=45)



# Max Meebit Price per Day in ETH
data = meebit_sales_df[['timestamp', 'total_price']].resample('D', on='timestamp').max()['total_price']
ax = data.plot(figsize=(18,6), color="red", linewidth=1, marker='o', markerfacecolor='grey', markeredgewidth=0)

ax.set_alpha(0.8)
ax.set_title("Timeline of Max Meebit Price in ETH", fontsize=18)
ax.set_ylabel("Max Price in ETH", fontsize=18);

dates = list(data.index)
values = list(data.values)

for i, j in zip(dates, values):
    ax.annotate(s="{:.0f}".format(j), xy=(i, j+30), rotation=45)



print("There are %d unique Meebit sellers." % len(meebit_sales_df['seller_address'].unique()))
print("There are %d unique Meebit buyers." % len(meebit_sales_df['buyer_address'].unique()))


# Get top 10 Buyers
buyers = []
for buyer_address in meebit_sales_df['buyer_address'].value_counts().index[:10]:
    buyer_data = {}
    buyer_data['buyer_address'] = buyer_address
    buyer_data['buyer_username'] = meebit_sales_df[meebit_sales_df['buyer_address'] == buyer_address]['buyer_username'].iloc[0]
    buyer_data['number_buys'] = len(meebit_sales_df[meebit_sales_df['buyer_address'] == buyer_address])
    buyer_data['min_price'] = meebit_sales_df[meebit_sales_df['buyer_address'] == buyer_address]['total_price'].min()
    buyer_data['max_price'] = meebit_sales_df[meebit_sales_df['buyer_address'] == buyer_address]['total_price'].max()
    buyer_data['mean_price'] = meebit_sales_df[meebit_sales_df['buyer_address'] == buyer_address]['total_price'].mean()
    buyers.append(buyer_data)
    
pd.DataFrame(buyers)


# Get Top 10 Meebits Sellers
sellers = []
for seller_address in meebit_sales_df['seller_address'].value_counts().index[:10]:
    seller_data = {}
    seller_data['seller_address'] = seller_address
    seller_data['seller_username'] = meebit_sales_df[meebit_sales_df['seller_address'] == seller_address]['seller_username'].iloc[0]
    seller_data['number_sales'] = len(meebit_sales_df[meebit_sales_df['seller_address'] == seller_address])
    seller_data['min_price'] = meebit_sales_df[meebit_sales_df['seller_address'] == seller_address]['total_price'].min()
    seller_data['max_price'] = meebit_sales_df[meebit_sales_df['seller_address'] == seller_address]['total_price'].max()
    seller_data['mean_price'] = meebit_sales_df[meebit_sales_df['seller_address'] == seller_address]['total_price'].mean()
    sellers.append(seller_data)
    
pd.DataFrame(sellers)



# Intersection of Top 10 Buyers and Top 10 sellers
top_10_buyers = meebit_sales_df['buyer_address'].value_counts().index[:10]
top_10_sellers = meebit_sales_df['seller_address'].value_counts().index[:10]
print(list(set(top_10_buyers) & set(top_10_sellers)))



# Getting Number of Sales between same Buyers and Sellers
(meebit_sales_df['seller_address'] + meebit_sales_df['buyer_address']).value_counts().value_counts()


