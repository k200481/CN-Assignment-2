from ctypes import util
from dataclasses import field
from select import select
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
                self.blacklist.append(gethostbyname(host.strip()))
            except:
                pass
        self.listener = socket(AF_INET, SOCK_STREAM)
        self.connections : list[threading.Thread] = []
        self.logger = server_logger('logs/info.log', 'logs/error.log', 'logs/dumps.log')

    def start(self, ip, port):
        addr = (ip, port)
        self.listener.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.listener.bind(addr)
        self.listener.listen(5)
        threading.Thread(target=self._listen).start()
    
    def _listen(self):
        while True:
            c, ret_addr = self.listener.accept()
            self.connections.append(threading.Thread(target=self._new_connection_handler, args=[c]))
            self.connections[len(self.connections) - 1].start()

    def _new_connection_handler(self, client : socket):
        req_bytes = client.recv(4096)
        if req_bytes == b'':
            client.close()
            return

        try:
            first_line = req_bytes.split(b'\r\n')[0].decode()
            first_line_split = first_line.split(' ')
            req_type = first_line_split[0]
            hostname = utility.extract_hostname(first_line_split[1])
            port = utility.get_portnum(first_line_split[1])

            if gethostbyname(hostname) in self.blacklist:
                client.close()
                return

            target = socket(AF_INET, SOCK_STREAM)
            target.connect((hostname, port))

            if req_type == 'CONNECT':
                self._https_connection(client, target, req_bytes)
            self._http_connection(client, target, req_bytes)
        except Exception as e:
            self.logger.log_error(e)
            self.logger.log_dump(req_bytes)
            return utility.get_error_page('Error Loading page', f'{e}').encode('utf-8')
        
        self.logger.log_info('Exiting')
    
    def _http_connection(self, client : socket, target : socket, req : bytes) -> None:
        file = self._process_http_request(client, target, req)
        while True:
            rlist, wlist, xlist = select([client, target], [], [])
            if client in rlist:
                req = client.recv(4096)
                if req == b'':
                    break
                file = self._process_http_request(client, target, req)
            if target in rlist:
                res = target.recv(4096)
                if res == b'':
                    break
                client.send(res)
                file.write(res)
    
    def _process_http_request(self, client : socket, target : socket, req : bytes):
        first_line = req.split(b'\r\n')[0].decode()
        first_line_split = first_line.split(' ')
        url = utility.extract_url(first_line_split[1])
        cache_filename = url.replace('/', '_')
        data = self.load_cache(cache_filename)
        if data: # state 1 requesting, as the current request was fulfilled
            client.send(data)
            self.logger.log_info(f'[CACHE HIT ] {first_line}')
            return None
        # state 2 responding + caching, as the current request was not pre-cached
        file = open(f'cache/{cache_filename}', 'wb')
        target.send(req)
        self.logger.log_info(f'[CACHE MISS] {first_line}')
        return file

    # forwards given https req to given hotname:port and returens the response
    def _https_connection(self, client : socket, target : socket, req: bytes):
        reply = 'HTTP/1.0 200 Connection Established\r\nProxy-agent: K200481_K20\r\n\r\n'
        client.send(reply.encode('utf-8'))

        while True:
            rlist, w, x = select([client, target], [], [], 0)
            if target in rlist:
                res = target.recv(4096)
                if res == b'':
                    break
                client.send(res)
            if client in rlist:
                req = client.recv(4096)
                if req == b'':
                    break
                target.send(req)

    def load_cache(self, filename) -> bytes:
        try:
            return open(f"cache/{filename}", 'rb').read()
        except:
            return None