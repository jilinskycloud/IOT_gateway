import httplib2
import json
import os
import urllib
import subprocess
import time
import redis
from urllib import request

class Vupdate:
	def __init__(self):
		with open("/www/wpScripts/_configs/path_conf.json") as json_file:
			_paths = json.load(json_file)
		self.log_path = _paths['p_update_log']
		self.sensor_conf = _paths['gw_conf_new_']
		self.Xcount = 0
		self.input_file = open(self.sensor_conf)
		self.r_sensor_conf = json.load(self.input_file)
		self.r_sensor_conf = self.r_sensor_conf["gw_data"][0]
		self.input_file.close()
		self.conn  = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True, password="LoRaDB")
		self.http = httplib2.Http(".cache",  disable_ssl_certificate_validation=True)

	############################################################
	#---  LOG BLOCK
	def log(self,log_str):                                                                                                                                                                                                        
	    #print("Log Function...........:: ",Xcount)
	    log_str = str(log_str)+" \n"                                                                                                   
	    self.Xcount = self.Xcount + 1                                                                                                              
	    if os.path.exists(self.log_path) == False:                                                                                             
	        #print("Log File not exist Creating it")                                                                                         
	        open(self.log_path, "w").close()                                                                                                   
	    with open(self.log_path, 'a') as outfile:                                                                                                  
	        outfile.write(log_str)                                                                                                     
	    if self.Xcount > 500:                                                                                                                       
	        cmd_rm = "rm "+ self.log_path                 
	        os.system(cmd_rm) 
	        self.Xcount = 0                                                                        
	    return  
	#---  END-BLOCK

	############################################################
	#---  Update LOOP BLOCK
	def update_f(self):
		self.log("4 ==> update_f Function...")
		url_ = "http://192.168.1.75/php_code/receive_post_value.php"
		body = {'distance':'123'}
		version = self.r_sensor_conf["version"] #"v-0.001"
		wget_cmd  = "wget http://192.168.1.75/php_code/gw-002.zip  -P /www/tmp_test" #"wget "+ self.r_sensor_conf["wget_url"]+" -P /www/tmp_test" 
		unzip_cmd = "unzip -q /www/tmp_test/gw-002.zip -d /www/tmp_test/test_set/"
		setup_cmd = "python3 /www/tmp_test/test_set/gw-002/setup.py"
		#print(version)
		#print(wget_cmd)
		while(1):
			try:
				time.sleep(1)
				content = self.http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
				content = str(content.decode("utf-8"))
				cn = content[0:7]
				self.log("No New Update :"+cn)
				#print("No New Update :",cn)
				#rec_pkt = json.loads(content)
				if cn != version:
					self.log("Update Available. Going to Update Package :: "+cn)
					if os.path.exists("/www/tmp_test/test_set/gw-002") == True :
						os.system("rm -r /www/tmp_test/test_set/gw-002")
					if os.path.exists("/www/tmp_test/gw-002.zip") == True:
						os.system("rm -r /www/tmp_test/gw-002.zip")
					os.system(wget_cmd)
					os.system(unzip_cmd)
					os.system(setup_cmd)
					self.conn.flushall()
					#os.system("reboot")
					version = cn
					time.sleep(20)
			except Exception as e:
				print("Exception:",e)
				pass		
	#---  END-BLOCK

############################################################
#---   Main BLOCK
def main(obj):
	obj.log("3 ==> update Main Function...")
	obj.update_f()
	
##MAIN FUNCTION
if __name__ == '__main__':
	time.sleep(60)
	obj = Vupdate()
	obj.log("1 ==> ~~ HEART-BEAT DAEMON ~~")
	obj.log("2 ==> Going to run Main Function")                       
	main(obj)
#---   END-BLOCK
