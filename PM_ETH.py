import os
import json
import socket
from tqdm import tqdm
from threading import Thread
from binascii import hexlify

request = (json.dumps({"id":0,"jsonrpc":"2.0","method":"control_gpu"}) + '\n').encode()
result = []

hosts = open('hosts.txt').read().split('\n')
hosts = list(set(hosts))
if '' in hosts:
    hosts.remove('')
print(len(hosts))

def checkMiner(host):
    try:
        if ':' in host:
          host = host.split(':')
          miner = (host[0], int(host[1]))
        else:
          miner = (host, 3333)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        sock.settimeout(3)
        sock.connect(miner)
        sock.send(request)
        resp = sock.recv(2048).decode()
        sock.close()
        if ('"result":false,"error":null}' in resp) or ('"code":-32601,"message":"Method not found"') in resp:
            result.append("{}:{}\t{}".format(miner[0], miner[1], resp))
            print("{}:{}\t{}".format(miner[0], miner[1], resp))
    except Exception as e:
        pass

at_a_time = 2000
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