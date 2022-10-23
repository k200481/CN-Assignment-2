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
            #self._client_handler(c, ret_addr)
            threading.Thread(
                target=self._client_handler, 
                args=[self.clients[len(self.clients) - 1], ret_addr]
            ).start()

    def _client_handler(self, client : socket, ret_addr):
        #self.logger.log_info(f'{ret_addr[0]}:{ret_addr[1]} Connected')
        req_bytes = client.recv(4096)
        if req_bytes == b'':
            #print(f'[{id}] [ERROR] Empty request from {ret_addr}')
            client.close()
            return
        
        try:
            self._req_handler(client, req_bytes)
        except Exception as e:
            self.logger.log_error(e)
            self.logger.log_dump(req_bytes)
            return utility.get_error_page('Error Loading page', f'{e}').encode('utf-8')
    
    def _req_handler(self, client: socket, req_bytes: bytes) -> None:
        req = req_bytes.decode('utf-8').split('\r\n')[0]
        #req = str(req_bytes).split('\\r')[0]
        hostname = utility.extract_hostname(req)
        port = utility.get_portnum(req)
        req_type = utility.extract_request_type(req)
        #http_ver = utility.extract_http_ver(req)

        if gethostbyname(hostname) in self.blacklist:
            self.logger.log_info(f'{req} Blocked')
            client.send(utility.get_error_page('Permission Denied', 
                'The website you are trying to access is blacklisted').encode('utf-8')
            )
            client.close()
            return

        if req_type == 'CONNECT':
            self._https_request(client, hostname, port, req_bytes)
        else:
            self._http_req(client, hostname, port, req_bytes)
    
    def _http_req(self, client : socket, hostname : str, port : int, req : bytes) -> None:
        target = socket(AF_INET, SOCK_STREAM)
        target.connect((hostname, port))

        target.setblocking(0)
        client.setblocking(0)

        data = b''
        cache_flag = False
        old_req = b''
        while True:
            try:
                if req != b'':
                    cached_data = self.retrieve(req)
                    if cached_data == None or cached_data == b'':
                        target.send(req)
                        cache_flag = False
                    else:
                        cache_flag = True
                    self.logger.log_dump(req)
                    if data != b'':
                        self.logger.log_info(f'{req} Cache Miss')
                        self.cache(req, data)
                        data = b''
                    else:
                        self.logger.log_info(f'{req} Cache Miss')
                    old_req = req
                    req = b''
                if cache_flag:
                    res = cached_data
                    self.logger.log_info(f'{old_req} Cache Hit')
                    cache_flag = False
                else:
                    res = target.recv(4096)
                    data = data.join([res])
            except:
                pass
            try:
                if res != b'':
                    client.send(res)
                    self.logger.log_dump(res)
                    res = b''
                req = client.recv(4096)
            except:
                pass

    # forwards given https req to given hotname:port and returens the response
    def _https_request(self, client : socket, hostname : str, port : int, req: bytes):
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