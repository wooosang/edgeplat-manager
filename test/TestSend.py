import json
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3)
sock.connect(('localhost', 8080))
sock.sendall(json.dumps({'command':'config'}).encode())
result = sock.recv(1)
print('Config result: {}'.format(result))
sock.sendall(json.dumps({'command':'subscribe'}).encode())
result = sock.recv(1)
print('Sbuscribe result: {}'.format(result))
sock.close()