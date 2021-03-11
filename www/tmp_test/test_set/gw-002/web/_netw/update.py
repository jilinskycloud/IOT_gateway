import httplib2
import json
import os
import urllib
import subprocess
import time
import redis
from urllib import request

global Xcount
Xcount = 0

############################################################
#---  LOG BLOCK
def log(log_str):                                                                                                                  
    global Xcount                                                                                        
    #print("in log...........:: ",Xcount)
    log_str = str(log_str)+" \n"                                                                                                   
    Xcount = Xcount+1                                                                                                              
    if os.path.exists("/tmp/update_daemon.log") == False:                                                                                             
        #print("Log File not exist CEATING IT")                                                                                         
        open("/tmp/update_daemon.log", "w").close()                                                                                                   
    with open('/tmp/update_daemon.log', 'a') as outfile:                                                                                                  
        outfile.write(log_str)                                                                                                     
    if Xcount > 10000:                                                                                                                              
        os.system("rm /tmp/update_daemon.log")
        Xcount = 0                                                                        
    return  
#---  END-BLOCK

############################################################
#---  Update LOOP BLOCK
def update_f():
	global Xcount 
	conn  = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True, password="LoRaDB")
	http = httplib2.Http(".cache",  disable_ssl_certificate_validation=True)
	url_ = "http://192.168.1.75/php_code/receive_post_value.php"
	body = {'distance':'123'}
	version = "v-0.001"
	wget_cmd  = "wget http://192.168.1.75/php_code/web.zip  -P /www/tmp_test"
	unzip_cmd = "unzip -q /www/tmp_test/web.zip -d /www/tmp_test/"
	cp_cmd    = "cp -r /www/tmp_test/web /www/tmp_test/test_set"
	per_cmd   = "chmod 777 /www/tmp_test/test_set/web/_netw/receive"
	rmf_cmd1   = "rm /www/tmp_test/web.zip"
	rmf_cmd2   = "rm -r /www/tmp_test/web"

	while(1):
		time.sleep(1)
		content = http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
		content = str(content.decode("utf-8"))
		cn = content[0:7]
		log("No New Updates"+cn)
		Xcount = Xcount+1
		#rec_pkt = json.loads(content)
		if cn != version:
			Xcount = Xcount+1
			log("Going to Update Package :: "+cn)
			os.system(wget_cmd)
			os.system(unzip_cmd)
			os.system(cp_cmd)
			os.system(per_cmd)
			os.system(rmf_cmd1)
			os.system(rmf_cmd2)
			#conn.flushall()
			#os.system("reboot")
			version = cn
			time.sleep(5)
#---  END-BLOCK


############################################################
#---   Main BLOCK
def main():
	update_f()
	
##MAIN FUNCTION
if __name__ == '__main__':
	log("HEART-BEAT DAEMON ~~")
	while True:
		if os.path.exists("/var/run/ProcLevel.pid") == True:
			f = open("/var/run/ProcLevel.pid","r")                                                   
			pNo = f.read()
			f.close() 
			if "5" == "5":
				pNo = "6"
				log("Going To run Main Function")
				f= open("/var/run/ProcLevel.pid","w+")
				f.write(pNo)                                                      
				f.close()                        
				main()
#---   END-BLOCK
