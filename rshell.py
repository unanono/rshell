#!/usr/bin/env python 
# -*- coding: utf-8 -*- 

import sys

from optparse import OptionParser
from rshell_core import rshell

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


def main():
    a = rshell(shell_url, proxy)
    a.prompt = 'rshell:~ '
    if options.s:
        a.print_payload()
    else:
        a.cmdloop()

if __name__ == '__main__':
    main()
