import json
import requests

# Get NFT project opensea html
opensea_html = "https://opensea.io/collection/mushrohms"

# Get NFT project Contract address and toen ID
contract_address = "0x133ba8f869f3ae35a5ca840ba20acfa31b0e2a61"
token_id = 99

# ReadContract -> tokenURI -> tokenID (query)
etherscan_addr = "https://etherscan.io/address/0x133ba8f869f3ae35a5ca840ba20acfa31b0e2a61#readContract"

# THIS IS WHAT WE NEED
ipfs_addr = "https://mushrohms.mypinata.cloud/ipfs/Qmeir9woe1ojVDAHdxJA6nRNC3v6KcFDptY7rQTsGA2M26/99.json"

x = json.loads(requests.get(ipfs_addr).text)

print(x)

# Should we do some statistical preprocessing up front? 
# E.g. Make the model not have to learn to count and divide, just present it with 
# probabilities and statistics on traits? (or in addition?!)