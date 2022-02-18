import requests
import json

url = "https://api.opensea.io/api/v1/collection/mushrohms"

response = requests.request("GET", url)

collection_data = json.loads(response.text)

print(collection_data['collection']['traits'])