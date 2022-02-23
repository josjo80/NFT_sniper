import requests
import json
import pandas as pd
import numpy as np
import pickle


def CallOpenSea(url):
    'Calls OpenSea and returns collection metadata'
    response = requests.request("GET", url)
    collection_data = json.loads(response.text)
    return collection_data

#print(collection_data['collection']['traits'])

def CreateVocab(collection_data):
    'Creates vocabulary for oneHot encoder'
    [vocab] = pd.json_normalize(collection_data['collection']['traits'], sep='.').to_dict(orient='records')
    #Force all vocab to be lowercase
    vocab = {k.lower(): v for k, v in vocab.items()}
    #print(vocab.keys())
    return list(vocab.keys())

def oneHot(sequences, vocabulary):
    results = np.zeros((len(sequences), len(vocabulary)))
    for i, sequence in enumerate(sequences):
        for ii, feat in enumerate(vocabulary):
            #print('sequence', sequence, 'feat', feat)
            if str(feat) in sequence:
                #print('True')
                results[i,ii] = 1.
    
    return results


def collect_nfts(max_num, base_link):
    # Collect all available json data for each token_id from IPFS
    xs = {}
    units_traits = []
    units = []
    for i in range(max_num):
        ipfs_addr = base_link + str(i)# + '.json'
        try:
            # Grab JSON directly from ipfs
            x = json.loads(requests.get(ipfs_addr).text)
            xs[x['name']] = x
            #print("Success!")
            #print(x)
            trait_list = [e['trait_type'].lower() + '.' + e['value'].lower() for e in x['attributes']]
            #print('Trait list')
            #print(trait_list)
            units_traits.append(trait_list)
            
        except:
            pass
        #print("unit traits")
        #print(units_traits)
    return units_traits


url = "https://api.opensea.io/api/v1/collection/pudgypenguins"

collection_data = CallOpenSea(url)

vocab = CreateVocab(collection_data)
#print(len(vocab))

# Get NFT project opensea html
opensea_html = "https://opensea.io/collection/pudgypenguins" #mushrohms

# Get NFT project Contract address and token ID
contract_address = "0xbd3531da5cf5857e7cfaa92426877b022e612cf8" # 0x133ba8f869f3ae35a5ca840ba20acfa31b0e2a61"
token_id = 99

# ReadContract -> tokenURI -> tokenID (query)
etherscan_addr = "https://etherscan.io/address/{}#readContract".format(contract_address)

# MANUAL LABOR: Open a Web Browser
# Copy down 1. MAX_<PROJ_NAME> (int range to iterate over later)
# Scroll to 7. baseTokenURI and COPY THE RESULTANT JSON PATH

# EXAMPLE: THIS IS WHAT WE NEED
max_nfts = 8888
base_uri  = "https://ipfs.io/ipfs/QmWXJXRdExse2YHRY21Wvh4pjRxNRQcWVhcKw4DLVnqGqs/" #  "https://mushrohms.mypinata.cloud/ipfs/Qmeir9woe1ojVDAHdxJA6nRNC3v6KcFDptY7rQTsGA2M26/"

all_num_units_traits = collect_nfts(max_nfts, base_uri)
one_hot_units = oneHot(all_num_units_traits, vocab)


with open(r'./data/nfts.pickle', 'wb') as f:
    pickle.dump(one_hot_units, f)