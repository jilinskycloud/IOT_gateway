import redis
import socket
import time
import os
import json

class ReadDist:
	def __init__(self):
		self.soc_list = []
		self.Xcount = 0
		self.r_sensor_conf = ''                                      
		self.conn = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True, password="LoRaDB")
		with open("/www/wpScripts/_configs/path_conf.json") as json_file:
			_paths = json.load(json_file)
		self.log_path = _paths['p_readdist_log']
		self.sensor_conf = _paths['sensor_conf_']
		
	############################################################
	#---  Read Sockets From Sensor Config BLOCK
	def read_sock(self):
	  input_file = open(self.sensor_conf)
	  self.r_sensor_conf = json.load(input_file)
	  self.r_sensor_conf = self.r_sensor_conf["sensors_data"]
	  for SN in self.r_sensor_conf:
	    if SN['ST'] == "distance":
	      self.soc_list.append(SN['sn_id'])
	#---  END-BLOCK

	############################################################
	#---  LOG BLOCK
	def log(self,log_str):
	    #print("Log Function...", Xcount)
	    log_str = str(log_str)+" \n"
	    self.Xcount = self.Xcount + 1               
	    if os.path.exists(self.log_path) == False:                                                                                             
	        #print("Log File not exist Creating it")                                                                                         
	        open(self.log_path, "w").close()                                                                                                   
	    with open(self.log_path, 'a') as outfile:                                                                                                  
	        outfile.write(log_str)                                                                                                     
	    if self.Xcount > 700:
	        cmd_rm = "rm " + self.log_path                 
	        os.system(cmd_rm)                                                                                                                              
	        self.Xcount = 0                                                                        
	    return  
	#---  END-BLOCK

	############################################################
	#---  Read Distance Socket BLOCK
	def read(self):
		self.log("4 ==> read Function...")
		self.read_sock()
		data = "0|0"
		print("Sockets List", self.soc_list)
		srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                   
		srvsock.settimeout(3)
		#print("Socket List ::",soc_list) 
		while(1):
			try:
				for SN in self.soc_list:
					_socket_ = SN 
					srvsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                                                           
					srvsock.settimeout(3)
					#print("Socket Read from file:: ",_socket_)
					socket_ = _socket_.split(":")
					print("IP :: ", socket_[0])
					print("PORT :: ", socket_[1])
					MESSAGE=bytes("M0\r\n", 'utf-8')
					#####################################################
					srvsock.connect((socket_[0], int(socket_[1])))
					i = time.time()+60
					while(time.time() <= i):
						srvsock.sendall(MESSAGE)
						data = srvsock.recv(4096).decode("utf-8")
						print("This is the data :: ",data)
						if len(data) !=0:
							a = float(data.split(',')[1]) / 1000.00
							#print("Read Data from Socket:: ",a)
							self.conn.lpush(_socket_, str(a))
						time.sleep(0.2)
					r_sum = sum((float(i) for i in self.conn.lrange(_socket_, 0, -1)))
					r_len  = int(self.conn.llen(_socket_))
					r_avg = str(r_sum/r_len)
					r_max = max((float(i) for i in self.conn.lrange(_socket_, 0, -1)))
					r_min = min((float(i) for i in self.conn.lrange(_socket_, 0, -1)))
					x = str(r_avg)+"|"+str(r_max)+"|"+str(r_min)+"|"+str(int(time.time()))
					### Save To the Redis
					dist_set = {_socket_:x} #0 index is AVG, index 1 is MAX, index 2 is MIN and index 3 is read time
					x = _socket_+"|"+x
					self.conn.hmset("sensor_data", dist_set)
					stt = {socket_:"OK"}
					self.conn.hmset("sensor_stt", stt)
					self.conn.expire("sensor_stt", 60)
					self.conn.lpush("dist_logs", x)
					self.conn.ltrim("dist_logs",0,500)
					self.log("Distance avg reading :: "+str(r_avg)+"r_len: "+str(r_len)+"r_max: "+str(r_max)+"r_min: "+str(r_min))
					#print("avg: ",r_avg,"r_len: ",r_len,"r_max: ",r_max,"r_min: ",r_min)	
					self.conn.delete(_socket_)
					srvsock.close()
			except Exception as e:
				self.read_sock() 
				print("Exception:",e)
				pass
	#---  END-BLOCK

def main(obj):
	obj.log("3 ==> readDist Main Function.")
	obj.read()

if __name__ == '__main__':
	time.sleep(10)
	obj = ReadDist()
	obj.log("1 ==> ~~ READ DISTANCE DAEMON ~~")
	while True:
		try:
			if os.path.exists("/var/run/ProcLevel.pid") == True:
				f = open("/var/run/ProcLevel.pid","r")                                                   
				pNo = f.read()
				f.close() 
				if pNo == "1":
					pNo = "2"
					obj.log("2 ==> Going To run Main Function")
					f= open("/var/run/ProcLevel.pid","w+")
					f.write(pNo)                                                      
					f.close()
					main(obj)
		except Exception as e:
			obj.read_sock() 
			print("Exception:",e)
			pass
#---  END-BLOCK
