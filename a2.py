import argparse
from socket import gethostbyname
import proxy_server
import utility

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('ip')
    parser.add_argument('port')
    args = parser.parse_args()

    while True:
        print('Config:')
        print('1: Add to Blackist')
        print('2: Start Server')
        c = int(input('Choice: '))
        if c == 2:
            break
        elif c == 1:
            while True:
                blacklist_file = open('blacklist.txt', 'a')
                try:
                    addr = input('Enter website host name [empty line to exit]: ')
                    if not addr:
                        break
                    hostname = utility.extract_hostname(addr)
                    ip = gethostbyname(hostname)
                    blacklist_file.write(f'{addr}\n')
                except Exception as e:
                    print(e)
                blacklist_file.close()

    ps = proxy_server.proxy_server()
    ps.start(args.ip, int(args.port))