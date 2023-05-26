import os
import json
import socket
from tqdm import tqdm
from threading import Thread
from binascii import hexlify

request = (json.dumps({"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}) + '\n').encode()
result = []

hosts = open('hosts.txt').read().split('\n')
hosts = list(set(hosts))
if '' in hosts:
    hosts.remove('')
print(len(hosts))

def checkMiner(host):
    try:
        host = host.split(':')
        miner = (host[0], int(host[1]))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        sock.settimeout(5)
        sock.connect(miner)
        sock.send(request)
        resp = sock.recv(2048).decode()
        sock.close()
        if 'ethminer' in resp:
            result.append("{}:{}\t{}".format(miner[0], miner[1], resp))
    except Exception as e:
        pass

at_a_time = 1000
chunks = [hosts[i:i + at_a_time] for i in range(0, len(hosts), at_a_time)]

for chunk in tqdm(chunks):
    threads = []
    for ip in chunk:
        thread = Thread(target=checkMiner, args=(ip,))
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
print(len(result))

final = open('report.txt', 'a')
for r in result:
    final.write(r)
final.close()
