import urllib2
import ssl
from urlparse import urlparse
import httplib


#ssl.create_default_context()

def do_request(url, data, proxy):
    if proxy:
        proxy_handler = urllib2.ProxyHandler({'https': '{0}'.format(proxy)})
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)
    context = None
    if url and url.find("https://") >= 0:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    try:
        if data:
            f = urllib2.urlopen(url, data, context=context)
        else:
            f = urllib2.urlopen(url, context=context)
        return f.read()
    except:
        return None


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
