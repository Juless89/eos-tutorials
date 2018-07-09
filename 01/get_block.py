import requests
import sys

block = sys.argv[1]
api_endpoint = 'http://api.eosnewyork.io'
api_request = '/v1/chain/get_block'
url = api_endpoint + api_request
parameters = '{"block_num_or_id":' + f'{block}' + '}'

print(requests.post(url=url, data=parameters).text)
