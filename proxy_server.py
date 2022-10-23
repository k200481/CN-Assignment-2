from socket import *
import threading
from server_logging import server_logger
import utility

class proxy_server:
    def __init__(self) -> None:
        self.blacklist : list[str] = []
        blacklisted_hosts = open('blacklist.txt', 'r').readlines()
        for host in blacklisted_hosts:
            try:
                self.blacklist.append(gethostbyname(host))
            except:
                pass
        self.listener = socket(AF_INET, SOCK_STREAM)
        self.clients : list[socket] = []
        self.logger = server_logger('logs/info.log', 'logs/error.log', 'logs/dumps.log')

    def start(self, ip, port):
        addr = (ip, port)
        self.listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.listener.bind(addr)
        self.listener.listen(5)
        self._listen()
    
    def _listen(self):
        while True:
            c, ret_addr = self.listener.accept()
            self.clients.append(c)
            threading.Thread(
                target=self._new_connection_handler, 
                args=[self.clients[len(self.clients) - 1], ret_addr]
            ).start()

    def _new_connection_handler(self, client : socket, ret_addr):
        req_bytes = client.recv(4096)
        if req_bytes == b'':
            client.close()
            return

        try:
            first_line = req_bytes.split(b'\r\n')[0].decode().split(' ')
            req_type = first_line[0]
            hostname = utility.extract_hostname(first_line[1])
            port = utility.get_portnum(first_line[1])

            if req_type == 'CONNECT':
                self._https_connection(client, hostname, port, req_bytes)
            self._http_connection(client, hostname, port, req_bytes)
        except Exception as e:
            self.logger.log_error(e)
            self.logger.log_dump(req_bytes)
            return utility.get_error_page('Error Loading page', f'{e}').encode('utf-8')
    
    def _http_connection(self, client : socket, hostname : str, port : int, req : bytes) -> None:
        target = socket(AF_INET, SOCK_STREAM)
        target.connect((hostname, port))

        target.setblocking(0)
        client.setblocking(0)

        cache_flag = False
        while True:
            try:
                if req != b'':
                    target.send(req)
                    self.logger.log_info(req)
                    filename = req.split(b'\r\n')[0].split(b' ')[1].decode().replace('/', '_')
                    data = self.load_cache(filename)
                    if data != None:
                        res = data
                        cache_flag = True
                    else:
                        file = open(f"cache/{filename}", 'wb')
                    req = b''
                if cache_flag == False:
                    res = target.recv(4096)
            except:
                pass
            try:
                if res != b'':
                    client.send(res)
                    if cache_flag == False:
                        file.write(res)
                        file.flush()
                    res = b''
                    cache_flag = False
                req = client.recv(4096)
            except:
                pass

    # forwards given https req to given hotname:port and returens the response
    def _https_connection(self, client : socket, hostname : str, port : int, req: bytes):
        target = socket(AF_INET, SOCK_STREAM)
        target.connect((hostname, port))

        reply = 'HTTP/1.0 200 Connection Established\r\nProxy-agent: K200481_K20\r\n\r\n'
        client.send(reply.encode('utf-8'))

        client.setblocking(0)
        target.setblocking(0)

        while True:
            try:
                req = client.recv(4096)
                target.sendall(req)
            except error as e:
                pass
            try:
                res = target.recv(4096)
                client.sendall(res)
            except error as e:
                pass
    
    def cache(self, req : str, data : bytes) -> None:
        try:
            url = req.decode().split(" ")[1]
            filename = url.strip("/").replace("/", "_")
            file = open(f"cache/{filename}", 'wb')
            file.write(data)
            file.close()
        except:
            pass
    def retrieve(self, req : str) -> bytes:
        try:
            url = req.decode().split(" ")[1]
            filename = url.strip("/").replace("/", "_")
            file = open(f"cache/{filename}", 'rb')
            return file.read()
        except Exception as e:
            #self.logger.log_error(e)
            return None
    def load_cache(self, filename) -> bytes:
        try:
            return open(f"cache/{filename}", 'rb').read()
        except Exception as e:
            self.logger.log_error(e)
            return None