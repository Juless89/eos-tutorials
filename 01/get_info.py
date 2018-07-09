import requests

api_endpoint = 'http://api.eosnewyork.io'
api_request = '/v1/chain/get_info'
url = api_endpoint + api_request

print(requests.get(url=url).json())
