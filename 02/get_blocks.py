import requests
import time
import sys
import json


# Extract and process the status_code. Return True only on success.
# Allow for dealing with issues depening on status_code
def verify_request(request):
    if request.status_code == 200:
        return True
    elif request.status_code == 500:
        error_code = json.loads(request.text)['error']['code']
        if error_code == 3100002:
            print('Waiting for blockchain to catch up\n')
            time.sleep(0.5)


# Retrieve block with number block_num
def get_block(block_num, s=None):
    # Global parameters used for API requests
    api_endpoint = 'http://mainnet.eoscanada.com'
    api_request = '/v1/chain/get_block'
    url = api_endpoint + api_request

    # API call takes one parameter: block_num_or_id for POST
    parameters = '{"block_num_or_id":' + f'{block_num}' + '}'

    print(f'Block {block_num}')

    # Keep making new requests until the request is returned succesfully.
    while True:
        if not s:
            request = requests.post(url=url, data=parameters)
            if verify_request(request):
                return request.text
        else:
            request = s.post(url=url, data=parameters)
            if verify_request(request):
                return request.text


# Iterate over the specified range based on the start_block and the block_count
# yield calls to get_block() to create iterable outout.
def stream_blocks(start_block, block_count, session=None):
    if session:
        s = requests.Session()

    for block_num in range(start_block, start_block + block_count):
        if not session:
            yield get_block(block_num)
        else:
            yield get_block(block_num, s)


# Iniate two streams starting at block 1 for 20 blocks. Use session in one of
# the two streams.
def perform_test():
    print('\nStarting performance test without session\n')
    start_time = time.time()
    for block in stream_blocks(1, 20):
        continue
    print(f'\nTook {time.time() - start_time} seconds for completion')

    start_time = time.time()
    print('\nStarting performance test with session\n')
    for block in stream_blocks(1, 20, session=True):
        continue
    print(f'\nTook {time.time() - start_time} seconds for completion')


if __name__ == '__main__':
    # Filter command line arguments, print error message when incorrect
    if len(sys.argv) == 3:
        start_block = int(sys.argv[1])
        block_count = int(sys.argv[2])
        for block in stream_blocks(start_block, block_count, True):
            print(block)
    elif len(sys.argv) == 1:
        perform_test()
    else:
        print('Takes two arguments <start_block> <end_block>')
        print('Running wihtout arguments will run performance test')
