import requests
import time
import sys


def verify_request(request):
    if request.status_code == 200:
        return True
    elif request.status_code == 500:
        print('Waiting for blockchain to catch up\n')
        time.sleep(0.5)


# Retrieve block with number block_num
def get_block(block_num, s=None):
    api_endpoint = 'http://mainnet.eoscanada.com'
    api_request = '/v1/chain/get_block'
    url = api_endpoint + api_request

    # API call takes one parameter: block_num_or_id
    parameters = '{"block_num_or_id":' + f'{block_num}' + '}'

    print(f'Block {block_num}')

    while True:
        if not s:
            request = requests.post(url=url, data=parameters)
            if verify_request(request):
                return request.text
        else:
            request = s.post(url=url, data=parameters)
            if verify_request(request):
                return request.text


def stream_blocks(start_block=1, block_count=20, session=None):
    start_time = time.time()

    if session:
        s = requests.Session()

    for block_num in range(start_block, start_block + block_count):
        if not session:
            yield get_block(block_num)
        else:
            yield get_block(block_num, s)

    print(f'\nTook {time.time() - start_time} seconds for completion')


def perform_test():
    print('\nStarting performance test without session\n')
    for block in stream_blocks():
        continue
    print('\nStarting performance test with session\n')
    for block in stream_blocks(session=True):
        continue


if __name__ == '__main__':
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
