import subprocess
import redis
import time
import os
import json

class ReadTemp:
	def __init__(self):
		self.Xcount = 0
		self.conn = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True, password="LoRaDB")
		with open("/www/wpScripts/_configs/path_conf.json") as json_file:
			_paths = json.load(json_file)
		self.log_path = _paths['p_readlora_log']

	############################################################
	#---  LOG BLOCK
	def log(self,log_str):                                                                                      
	    #print("Log Function...")
	    log_str = str(log_str)+" \n"                                                                                                   
	    self.Xcount = self.Xcount + 1                                                                                                              
	    if os.path.exists(self.log_path ) == False:                                                                                             
	        #print("Log File not exist creating it")                                                                                         
	        open(self.log_path, "w").close()                                                                                                   
	    with open(self.log_path , "a") as outfile:                                                                                                  
	        outfile.write(log_str)                                                                                                     
	    if self.Xcount > 700:
	        cmd_rm = "rm "+ self.log_path
	        os.system(cmd_rm)
	        self.Xcount = 0                                                                        
	    return  
	#---  END-BLOCK 

	############################################################
	#---  Read LoRa BLOCK
	def readLora(self):
		obj.log("4 ==> Read Lora Function...")
		self.conn.delete("sensor_data")                                                                                                       
		self.conn.delete("last_send_time") 
		while(1):
			try:
				cmd = "/www/wpScripts/_dataloggers/_includes/receive /dev/loraSPI1.0"
				proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
				(sn_data, err1) = proc.communicate()
				sn_data = sn_data.decode('utf-8')
				#print("Read-Daemon ==> Rceived Sensor Data ::", len(sn_data))
				if len(sn_data) != 0:
					self.log("Rceived Sensor Data :: "+sn_data)
					sn_data= sn_data.split('|')
					print("Rceived Sensor Data ::", sn_data)
					tm = time.time()
					temp_set = {sn_data[0]:sn_data[1]+"|"+str(int(time.time()))} #0 index is sensor id and index 1 is temperature
					#temp_set = sn_data[0]+"|"+sn_data[1]+"|"+str(int(time.time()))
					stt = {sn_data[0]:"OK",}
					self.conn.hmset("sensor_stt", stt)
					self.conn.expire("sensor_stt", 60)
					self.conn.hmset("sensor_data",temp_set)
					temp_set = sn_data[0]+"|"+sn_data[1]+"|"+str(int(time.time()))
					self.conn.lpush("temp_logs",temp_set)
					self.conn.ltrim("temp_logs", 0,500)
					sn_list = self.conn.lrange('sn_list',0,-1)
					if sn_data[0] not in sn_list:
						self.conn.lpush('sn_list',sn_data[0])
					sn_list = self.conn.lrange('sn_list',0,-1)
					#print(Sensor List :",sn_list)
			except Exception as e:
				print("Exception :",e)
				pass	
	#---  END-BLOCK 

############################################################
#--- Main BLOCK
def main(obj):
    obj.log("3 ==> Read Temperature Main Function.")
    obj.readLora()
	
if __name__ == '__main__':
	time.sleep(5)
	obj = ReadTemp()
	obj.log("1 ==> ~~ READ TEMPERATURE DAEMON ~~")
	pNo = "1"
	f= open("/var/run/ProcLevel.pid","w+")
	f.write(pNo)
	f.close()
	while True:
		try:
			obj.log("2 ==> Going to  run Main Function.")
			main(obj)
		except Exception as e:
			print("Exception :",e)
			pass
#---  END-BLOCK 
