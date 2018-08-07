#!/usr/bin/env python3

import sys
import argparse
import base64
import json
import qrcode
from urllib.parse import urlparse

DEFAULT_CONFIG = json.loads("""{"run_type":"client","local_addr":"127.0.0.1",
"local_port":1080,"remote_addr":"example.com","remote_port":443,"password":[
"password1"],"append_payload":true,"log_level":1,"ssl":{"verify":true,
"verify_hostname":true,"cert":"",
"cipher":"ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA:AES128-SHA:AES256-SHA:DES-CBC3-SHA",
"sni":"example.com","alpn":["h2","http/1.1"],"reuse_session":true,"curves":"",
"sigalgs":""},"tcp":{"keep_alive":true,"no_delay":true,"fast_open":true,
"fast_open_qlen":5}}""")

def fail(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

def encode(qr):
    try:
        config = json.load(sys.stdin)
        if config['run_type'] != 'client':
            fail('Please provide a client config')
        if ':' in config['remote_addr']:
            config['remote_addr'] = '[{}]'.format(config['remote_addr'])
        url = 'trojan://{}@{}:{}'.format(base64.b64encode(config['password'][0].encode()).decode() ,config['remote_addr'], config['remote_port'])
    except:
        fail('Invalid config')
    try:
        if qr:
            qrcode.make(url).save(sys.stdout, 'PNG')
        else:
            print(url)
    except:
        fail('Save failed')

def decode():
    url = urlparse(sys.stdin.read().strip('\n'))
    print(url)
    if url.scheme != 'trojan':
        fail('Not trojan URL')


def main():
    parser = argparse.ArgumentParser(description='Encode and decode trojan URLs from and to trojan config.')
    parser.add_argument('-d', '--decode', action='store_true', help='decode input')
    parser.add_argument('-q', '--qrcode', action='store_true', help='output qrcode')
    parser.add_argument('-i', '--input', default='-', metavar='in_file', help='input file (default: "-" for stdin)')
    parser.add_argument('-o', '--output', default='-', metavar='out_file', help='output file (default: "-" for stdout)')
    args = parser.parse_args()
    if args.qrcode:
        if args.decode:
            fail('Decoding QRCode is not supported')
        if args.output == '-':
            fail('Please output QRCode to a file')
    if args.input != '-':
        sys.stdin = open(args.input, 'r')
    if args.output != '-':
        if args.qrcode:
            sys.stdout = open(args.output, 'wb')
        else:
            sys.stdout = open(args.output, 'w')
    if args.decode:
        decode()
    else:
        encode(args.qrcode)

if __name__ == '__main__':
    main()
