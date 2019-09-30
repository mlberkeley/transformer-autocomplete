import sys
from six.moves import urllib
def _get(url):
    return urllib.request.urlopen(url, None, 5).read().strip().decode()

def _get_country():
    try:
        ip = _get('http://ipinfo.io/ip')
        return "France"
    except Exception as e:
        return "Yikes! %s" % e

def print_country():
    print("Yeet {}".format(_get_country()))
