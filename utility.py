import re
import socket

# extracts hostname from a given url(:portnum) string
def extract_hostname(string : str) -> str:
    return re.search(r'([a-z]|[0-9])+(\.([a-z]|[0-9])+)+', string).group(0)
# extracts portnum from a given url:portnum string
def extract_portnum(string) -> int:
    match_obj = re.search('(?<=\:)[0-9]{1,5}', string)
    if match_obj != None:
        return int(match_obj.group(0))
    return None
def extract_http_ver(string : str) -> str:
    return re.search(r'HTTP/[1-3]\.[0-9]', string).group(0)
def extract_request_type(string : str) ->str:
    return re.search(r'^[A-Z]+', string).group(0)
def extract_url(string : str):
    return re.search(r'(http|https):\/\/([a-z]|[0-9]|\.|\/|-)+', string).group(0)

# returns portnum from a given url:portnum string, 80 if none exists
def get_portnum(string : str):
    portnum = extract_portnum(string)
    if portnum == None:
        return 80
    return portnum

def get_error_page(title : str, msg : str) -> str:
    page = open('temp.html', 'r').read()
    return page.replace('error_title', title, 1).replace('error_message', msg, 1)
