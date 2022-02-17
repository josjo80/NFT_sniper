import json
import requests


# Get NFT project opensea html
opensea_html = "https://opensea.io/collection/mushrohms"

# Get NFT project Contract address and token ID
contract_address = "0x133ba8f869f3ae35a5ca840ba20acfa31b0e2a61"
token_id = 99

# ReadContract -> tokenURI -> tokenID (query)
etherscan_addr = "https://etherscan.io/address/{}#readContract".format(contract_address)

# MANUAL LABOR: Open a Web Browser
# Copy down 1. MAX_<PROJ_NAME> (int range to iterate over later)
# Scroll to 7. baseTokenURI and COPY THE RESULTANT JSON PATH

# EXAMPLE: THIS IS WHAT WE NEED
max_nfts = 1500
base_uri  = "https://mushrohms.mypinata.cloud/ipfs/Qmeir9woe1ojVDAHdxJA6nRNC3v6KcFDptY7rQTsGA2M26/"

# Collect all available json data for each token_id from IPFS
xs = {}
for i in range(max_nfts):
    ipfs_addr = base_uri + str(i) + '.json'
    try:
        # Grab JSON directly from ipfs
        x = json.loads(requests.get(ipfs_addr).text)
        xs[x['name']] = x
        print("Success!")
        print(x)
    except:
        pass

# TODO: store as json instead of pydict?
import pickle
with open('./output_dict', 'wb') as f:
    pickle.dump(xs, f)

# NOTE:
# Should we do some statistical preprocessing up front? 
# E.g. Make the model not have to learn to count and divide, just present it with 
# probabilities and statistics on traits? (or in addition?!)