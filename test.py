#!/usr/bin/env python3
"""
A simple test script for benchmarking the server
"""

import json
import requests
import time

data = [
    {'monolog/monolog': '*', 'cssjanus/cssjanus': '1.1.*'},
    {'wikimedia/cdb': '1.0.1', 'cssjanus/cssjanus': '1.1.0'},
    {'cssjanus/cssjanus': '1.*'},
    {'cssjanus/cssjanus': '*'},
]
start = time.time()
r = requests.post('http://localhost:5000/get', data={'data': json.dumps(data)}, stream=True)
with open('vendor-dl.tar.gz', 'wb') as f:
    for chunk in r.iter_content(1024):
        f.write(chunk)
print('Downloaded')
print('Took %s seconds.' % (time.time() - start))
