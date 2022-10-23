import socket

skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
skt.connect(('info.cern.ch', 80))

msg = 'GET http://info.cern.ch/ HTTP/1.1\r\n'
msg += 'Host: info.cern.ch\r\n'
msg += 'If-Modified-Since: Wed, 05 Feb 2014 16:00:31 GMT\r\n\r\n'

skt.send(msg.encode())
print(skt.recv(1024).decode())