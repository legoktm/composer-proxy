#!/usr/bin/env python3

from collections import defaultdict
from flask import Flask, request, send_file
import hashlib
import json
import os
import subprocess
import shutil

conf = {
    'COMPOSER_COMMAND': 'composer',
    'TEMP_DIRS': os.path.join(os.path.dirname(__file__), 'tmp')
}

app = Flask(__name__)


@app.route('/')
def home() -> str:
    return 'Hello world!'


def merge_dependencies(deps):
    merged = defaultdict(set)
    for depgroup in deps:
        for name, version in depgroup.items():
            merged[name].add(version)

    return dict([(name, ','.join(version)) for name, version in merged.items()])


@app.route('/get', methods=['POST'])
def get() -> str:
    if 'data' not in request.form:
        return 'No data provided'
    data = request.form['data']
    try:
        # [{'foo/bar':'1.2.3'}, {'bar/foo':'2.0.*'}]
        deps = json.loads(data)
    except ValueError as e:
        return 'Invalid JSON: %s' % str(e)
    merged_deps = merge_dependencies(deps)
    hash_ = hashlib.sha1(json.dumps(merged_deps).encode()).hexdigest()
    print(hash_)
    path = lambda x: os.path.join(conf['TEMP_DIRS'], hash_, x)
    if os.path.isfile(path('vendor.tar.gz')):
        return send_file(path('vendor.tar.gz'))
    os.mkdir(path(''))
    composer_params = ['--prefer-dist', '--no-dev', '--no-plugins', '--no-ansi']
    with open(path('composer.json'), 'w') as f:
        json.dump({
            'require': merged_deps
        }, f)
    cwd = os.getcwd()
    os.chdir(path(''))
    # Fetch dependencies...
    subprocess.check_call(['composer', 'install'] + composer_params)
    # Put the composer.lock file inside vendor for future reference
    shutil.copy('composer.lock', 'vendor/composer.lock')
    # Build tarball...
    subprocess.check_call(['tar', '-czPf', 'vendor.tar.gz', 'vendor'])
    os.chdir(cwd)
    return send_file(path('vendor.tar.gz'))


if __name__ == '__main__':
    app.run(debug=True)
