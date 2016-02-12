import urllib2
import ssl
from urlparse import urlparse
import httplib


#ssl.create_default_context()

def do_request(url, data, proxy):
    if proxy:
        print url, data, proxy
        proxy_handler = urllib2.ProxyHandler({'https': '{0}'.format(proxy)})
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)
    if url.find("http://") >= 0:
        context = None
    else:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    if data:
        f = urllib2.urlopen(url, data, context=context)
    else:
        f = urllib2.urlopen(url, context=context)
    
    return f.read()


def alternative_proxy_test():
    import socks
    import socket
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "proxy.cab.cnea.gov.ar", 1080)
    socket.socket = socks.socksocket
    print urllib2.urlopen('https://www.google.com.ar').read()


def do_request_hlib(url, data, proxy):
    parsed_url = urlparse(url)
    if proxy:
        (ip, port) = proxy.split(':')
        #con = httplib.HTTPConnection(parsed_url.netloc, parsed_url.port)
        if url.find("https:/") >= 0:
            con = httplib.HTTPSConnection(ip, int(port), context=ssl._create_unverified_context())
            con.set_tunnel(parsed_url.netloc, parsed_url.port)
        else:
            con = httplib.HTTPConnection(ip, int(port))
    else:
        url = parsed_url.path
        con = httplib.HTTPConnection(parsed_url.netloc, parsed_url.port)
    headers = {"Content-type": "application/x-www-form-urlencoded",
               "Accept": "text/plain"}
    if con:
        con.request('GET', url, data, headers)
        response = con.getresponse()
        if response.status == 200:
            return (response.status, response.read())
        else:
            #
            return (response.status, response.read())
    else:
        #
        return (None, None)
