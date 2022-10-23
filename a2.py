import argparse
import proxy_server

if __name__ == "__main__":
    ps = proxy_server.proxy_server()
    ps.start('localhost', 55555)

    #parser = argparse.ArgumentParser()
    #parser.add_argument('ip')
    #args = parser.parse_args()

    #listener_thread = threading.Thread(target=listener, args=[args.ip, 55555])
    #listener(args.ip, 55555)
