from pydoc import cli
import socket
# forwards given http req to given hotname:port and returens the response
def http_request(hostname : str, port : int, req: bytes) -> bytes:
    target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target.connect((hostname, port))
    target.send(req)
    res = target.recv(4096)
    return res

def http_req2(client : socket.socket, hostname : str, port : int, req : bytes) -> None:
    target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target.connect((hostname, port))

    target.setblocking(0)
    client.setblocking(0)

    while True:
        try:
            target.send(req)
            res = target.recv(4096)
        except:
            pass
        try:
            client.send(res)
            req = client.recv(4096)
        except:
            pass

# forwards given https req to given hotname:port and returens the response
def https_request(client : socket.socket, hostname : str, port : int, req: bytes):
    target = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    target.connect((hostname, port))

    reply = 'HTTP/1.0 200 Connection Established\r\nProxy-agent: K200481_K20\r\n\r\n'
    client.send(reply.encode('utf-8'))

    client.setblocking(0)
    target.setblocking(0)

    while True:
        try:
            req = client.recv(4096)
            target.sendall(req)
        except socket.error as e:
            pass
        try:
            res = target.recv(4096)
            client.sendall(res)
        except socket.error as e:
            pass