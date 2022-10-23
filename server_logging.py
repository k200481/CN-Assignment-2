import threading

class server_logger:
    def __init__(self, infofilename : str = None, errorfilename : str = None, dumpfilename : str = None) -> None:
        if infofilename == None:
            self.console_info = True
        else:
            self.console_info = False
            self.info_file = open(infofilename, 'w+')

        if errorfilename == None:
            self.console_error = True
        else:
            self.console_error = False
            self.error_file = open(errorfilename, 'w+')

        if dumpfilename == None:
            self.console_dump = True
        else:
            self.console_dump = False
            self.dump_file = open(dumpfilename, 'w+')
        pass

    def log_info(self, msg):
        line = f'[{threading.current_thread().native_id}] [INFO ] {msg}'
        if self.console_info:
            print(line)
        else:
            line += '\n'
            self.info_file.write(line)
            self.info_file.flush()
    
    def log_error(self, msg):
        line = f'[{threading.current_thread().native_id}] [ERROR] {msg}'
        if self.console_error:
            print(line)
        else:
            line += '\n'
            self.error_file.write(line)
            self.error_file.flush()
    
    def log_dump(self, msg):
        line = f'[{threading.current_thread().native_id}] [DUMP ] {msg}'
        if self.console_dump:
            print(line)
        else:
            line += '\n'
            self.dump_file.write(line)
            self.dump_file.flush()