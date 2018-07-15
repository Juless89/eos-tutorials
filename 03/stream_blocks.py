import requests
import time
import sys
import operator


class EOS():
    def __init__(self, start_block=None, block_count=None):
        self.block = start_block
        self.block_count = block_count
        self.s = requests.Session()
        self.nodes = ['http://mainnet.eoscanada.com',
                      'http://api-mainnet1.starteos.io',
                      'http://api.eosnewyork.io']
        self.test_api_endpoints()

        self.node_index = 0
        self.url = self.nodes[self.node_index]

    # Test all api_endpoints for the speed by retrieving 100 blocks and timing
    # Sort the api_endpoints by their speed
    def test_api_endpoints(self):
        results = []

        for url in self.nodes:
            self.url = url
            start_time = time.time()
            print(f'\nTesting: {url}')

            for block in self.stream_blocks(start_block=1, block_count=100):
                print(f'{self.block}/100', end='\r')

            end_time = time.time() - start_time
            results.append((url, end_time))
            print(f'Took {end_time:.4} seconds for completion')

        # Sort the results by their times
        results.sort(key=operator.itemgetter(1))

        # Extract only the urls to create a sorted nodes list
        self.nodes = [node[0] for node in results]
        print(self.nodes)

    def reset_api_endpoint(self):
        self.node_index = (self.node_index + 1) % len(self.nodes)
        self.url = self.nodes[self.node_index]
        self.s = requests.Session()
        print(f'New api_endpoint: {self.url}')

    # Retrieve global node information and extract the current head block num
    def get_head_block(self, irreversible=None):
        time.sleep(25/1000)

        api_call = '/v1/chain/get_info'
        address = self.url + api_call

        request_json = self.s.get(url=address).json()

        if not irreversible:
            return request_json['head_block_num']
        else:
            return request_json['last_irreversible_block_num']

    # Perform a POST request for a block with block_number block
    def get_block(self, block):
        api_call = '/v1/chain/get_block'
        params = '{"block_num_or_id":' + f'{block}' + '}'
        address = self.url + api_call

        # Check the status code for each request. Return text on succes:200.
        # Process in case of error:500.
        while True:
            address = self.url + api_call
            r = self.s.post(url=address, data=params)
            if r.status_code == 200:
                return r.text
            print(r.text)
            self.reset_api_endpoint()

    def stream_blocks(self,
                      start_block=None,
                      block_count=None,
                      irreversible=None):

        # set start_block
        if not start_block:
            start_block = self.block
        else:
            self.block = start_block

        # In case of a block_count set end_block
        if not block_count:
            end_block = None
        else:
            end_block = start_block + block_count - 1

        # Loop indefinitely
        while True:
            # retrieve head_block / last_irreversible_block
            head_block = self.get_head_block(irreversible)

            # define range of blocks to request
            for n in range(start_block, head_block + 1):
                # when end_block is reached exit the loop
                if end_block and n > end_block:
                    raise StopIteration()

                yield self.get_block(n)
                self.block += 1

            # set start_block for next cycle
            start_block = head_block + 1

    # Run a unending stream of blocks, either in current head_block mode
    # or in last_irreversible_block mode
    def run(self, irreversible=None):
        # Configure mode and set the current block accordingly
        if not irreversible:
            print('\nMode: head_block')
        else:
            print('\nMode: last_irreversible_block')
        self.block = self.get_head_block(irreversible)

        # Loop indefinitely
        while True:
            try:
                for block in self.stream_blocks(irreversible=irreversible):
                    print(f'Block {self.block}', end='\r')
            except Exception as error:
                    time.sleep(60)
                    print(repr(error))


if __name__ == '__main__':
    # Filter for command line arguments
    try:
        if len(sys.argv) == 2:
            eos = EOS()
            if sys.argv[1] == 'irreversible':
                eos.run(irreversible=True)
        elif len(sys.argv) == 1:
            eos = EOS()
            eos.run()
    except Exception as error:
        print('python stream_blocks.py to stream from current head_block')
        print('python stream_blocks.py irreversible to stream from current' +
              'last_irreversible_block')
