import httplib2
import json
import os
import signal
import urllib
import redis
import subprocess
import time
from _includes.sendLogs import MultiPartForm
from _includes.EncDec import EncDec
import io
import mimetypes
from urllib import request
import uuid
import socket
import base64


class HeartBeat:
	def __init__(self):
		self.conn = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True, password="LoRaDB")
		self.http = httplib2.Http(".cache",  disable_ssl_certificate_validation=True)
		self.HB = 'OFF'
		self.content = ""
		self.Xcount = 0
		self.statuscode = 0
		self.EncObj = EncDec()
		proc = subprocess.Popen(["hostname"], stdout=subprocess.PIPE, shell=True)
		(self.gw_id, err1) = proc.communicate()
		self.gw_id = self.gw_id.decode('utf-8')
		self.gw_id = self.gw_id.strip()
		self.hb_pid = "/var/run/hBeat.pid"
		self.pr_pid = "/var/run/ProcLevel.pid"
		self.r_sensor_conf = ''
		with open("/www/wpScripts/_configs/path_conf.json") as json_file:
			_paths = json.load(json_file)
		self.log_path = _paths['p_hb_log']
		self.sensor_conf = _paths['sensor_conf_']
		self.gw_conf = _paths['gw_conf_']
		signal.signal(signal.SIGUSR1, self.receive_signal)
		pidis = str(os.getpid())
		#print('heartbeat.py PID ==> ',pidis)
		self.log('heartbeat.py PID ==> '+pidis)
		f= open(self.hb_pid,"w+")
		f.write(pidis)
		f.close()
		self.status_()

	############################################################
	#---  Read Conf Block
	def  read_conf(self):
		self.r_sensor_conf = []
		input_file = open(self.sensor_conf)
		self.r_sensor_conf = json.load(input_file)
		self.r_sensor_conf = self.r_sensor_conf["sensors_data"]
		input_file.close()
		self.log("Read Sensor Configuration.")
	#---  END-BLOCK

	############################################################
	#---  LOG BLOCK
	def log(self,log_str):
	    #print("Log Function : ",self.Xcount)
	    log_str = str(log_str)+" \n"                                                                                                   
	    self.Xcount = self.Xcount + 1                                                                                                              
	    if os.path.exists(self.log_path) == False:                                                                                             
	        #print("Log File not exist Creating it Now")                                                                                         
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
	#---  Update Config BLOCK
	def status_(self):
		self.log("Heartbeat Status check.")
		r_gw_conf_ = json.load(open(self.gw_conf,'r'))
		r_gw_conf_ = r_gw_conf_["gw_data"]
		r_gw_conf_ = r_gw_conf_[0]
		#print("Check heart beat status: ", r_gw_conf_['hbeat_status'])
		if r_gw_conf_['hb_status'] == 1:
			self.HB = "ON"
			#print("Heartbeat Status is ON")
			self.log("Heartbeat Status is ON")
		else:
			self.HB = "OFF"
			#print("Heartbeat Status is OFF")
			self.log("Heartbeat Status is OFF")
		return self.HB
	#---  END-BLOCK

	############################################################
	#---   Send LOGS BLOCK
	def sendLogs(self):
		# Create tar.gz Log file 
		log_cmd = "tar -czvf /www/wpScripts/_connect/"+self.gw_id+"_Logs.tar.gz /var/process_logs/*"
		log_rm = "rm /www/wpScripts/_connect/"+self.gw_id+"_Logs.tar.gz"
		log_file = "/www/wpScripts/_connect/"+self.gw_id+"_Logs.tar.gz"
		os.system(log_cmd)
		#print("Send Log File to the server...")
		form = MultiPartForm()
		# Add a fake file
		form.add_field('gw_id', self.gw_id)
		file_name = self.gw_id+"_"+str(int(time.time()))+"_Logs.tar.gz"
		form.add_file('file', file_name, open(log_file,'rb')) 
		# Build the request, including the byte-string
		# for the data to be posted.
		data = bytes(form)
		r_gw_conf_ = json.load(open(self.gw_conf,'r'))
		r_gw_conf_ = r_gw_conf_["gw_data"]
		r_gw_conf_ = r_gw_conf_[0]
		down_logs_url = r_gw_conf_["log_url"]
		r = request.Request(down_logs_url, data=data)
		r.add_header('Content-type', form.get_content_type())
		r.add_header('Content-length', len(data))
		#print('Outgoing Data:')
		#for name, value in r.header_items():
		#	#print('{}: {}'.format(name, value))
		#	#print(r.data.decode('utf-8'))
		server_msg = request.urlopen(r).read().decode('utf-8')
		#print('Server Response ::', server_msg)
		self.log("Logs Sent to the Server.")
		os.system(log_rm)
		return server_msg
	#---  END-BLOCK


	############################################################
	#---   Delete sensor ID (SN_ID) BLOCK
	def delete_sn_id(self,del_SnId):
		der = "a" 
		ax = {}
		#print("Delete Id is 001:",del_SnId)
		with open(self.sensor_conf) as json_file: 
		  data = json.load(json_file) 
		  temp = data["sensors_data"]
		  #print("Delete Sensor Id temp 002: ",temp)
		for idx, SN in enumerate(temp):
			#print("File sn_id ::",SN['sn_id'] ,"Received sn_id :: 003",del_SnId)
			if SN['sn_id'] == del_SnId:
				der = idx
		#print("This is the index of der 004", der)
		if der != "a":
		  temp.pop(der)
		  #print("Specified sensor ID is Deleted!! 004")
		  self.log("Specified sensor id is Deleted.")
		ax['sensors_data'] = temp
		with open(self.sensor_conf,'w') as f: 
		  json.dump(ax, f, indent=4)
	#---   Del SN_ID BLOCK

	############################################################
	#---  Heart-Beat LOOP BLOCK
	def beat(self):
		#print("In heart beat Loop")
		send_once = 0
		self.log("4 ==> Heart-Beat beat() Function...")
		self.read_conf()
		while(1):
			if self.HB == "ON":
				try:
					for SN in self.r_sensor_conf:
						self.log("beat() Function for Loop Within while Loop...")
						#print("Delay time", SN['hb_interval'])
						time.sleep(int(SN["hb_interval"]))
						#url_ = SN["hb_api_address"]
						r_gw_conf_ = json.load(open(self.gw_conf,'r'))
						r_gw_conf_ = r_gw_conf_["gw_data"]
						r_gw_conf_ = r_gw_conf_[0]
						url_ = r_gw_conf_['heartbeat_url']
						##############################
						#---  First Time Send BLOCK
						if send_once == 0:
							sn_list = self.conn.lrange('sn_list',0,-1)
							#body = {'gw_id':self.gw_id,'statuscode':'', 'sn_list':sn_list}
							vl = {'gw_id':self.gw_id,'statuscode':'', 'sn_list':sn_list}
							body = {"encoded":self.EncObj.enc_data(str(vl))}
							print("Body::",body)
							while self.content != "sn_rec":
								self.content = self.http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body))[1]
								time.sleep(5)
								self.content = eval(base64.b64decode(self.EncObj.dec_data(eval(self.content.decode("utf-8")))).decode("utf-8"))
								print("First Time Send BLOCK Received data :: ", self.content)
								self.content = self.content['msg']
								print("First time Data send (sn_id) list first")
								self.log("First Time Sent (sn_list)")
							self.conn.flushall()
							send_once =  1
						#---  First Time Send BLOCK
						
						##############################
						#---  Normal Data Send BLOCK 
						vl = {'gw_id':self.gw_id,'statuscode':self.statuscode}
						body = {"encoded":self.EncObj.enc_data(str(vl))}
						#body = {'gw_id':self.gw_id,'statuscode':self.statuscode}
						print("Send Packet:: ", body)
						self.log("Normal Heart-Beat send Block")
						self.content = self.http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
						#self.content = self.content.decode("utf-8")
						self.content = eval(base64.b64decode(self.EncObj.dec_data(eval(self.content.decode("utf-8")))).decode("utf-8"))
						print("Received Packet :: ",self.content)
						#rec_pkt = json.loads(self.content)
						rec_pkt = self.content
						print("Received MSG from server :: ", rec_pkt)
						hb_stt = str(rec_pkt['code'])+"|"+str(int(time.time()))
						self.log("Ping status (stt) normal:: "+hb_stt)
						self.conn.hset("ping_stt", "hb_stt", hb_stt)
						self.statuscode = rec_pkt['statuscode']
						#---  Normal Data Send BLOCK 
						
						##############################
						#---  Server MSG related code 
						#print("Heart-Beat Daemon ==> MSG::",rec_pkt['msg'])
						if rec_pkt['msg'] == 'gw_reboot':
							self.log("Reboot command From Server")
							print("Reboot Command (Reboot the System)!")
							#body = {'gw_id':self.gw_id,'statuscode':self.statuscode}
							vl = {'gw_id':self.gw_id,'statuscode':self.statuscode}
							body = {"encoded":self.EncObj.enc_data(str(vl))}
							self.http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
							os.system("reboot")
						elif rec_pkt['msg'] == 'sn_config':
							self.log("Sensor Configuration Received from server writing it to file ...")
							self.statuscode = rec_pkt['statuscode']
							#body = {'gw_id':self.gw_id,'statuscode':self.statuscode}
							vl = {'gw_id':self.gw_id,'statuscode':self.statuscode}
							body = {"encoded":self.EncObj.enc_data(str(vl))}
							self.http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
							update_sn_id = rec_pkt['data']
							print("Sensor Config Received::",update_sn_id)
							update_sn_id['hb_api_address'] = update_sn_id['hb_api_address'].replace('\\','')
							update_sn_id['data_api_address'] = update_sn_id['data_api_address'].replace('\\','')
							self.delete_sn_id(update_sn_id['sn_id'])
							with open(self.sensor_conf) as json_file: 
								data = json.load(json_file) 
								temp = data["sensors_data"]
								cont = rec_pkt['data']
								temp.append(cont)
							with open(self.sensor_conf,'w') as f: 
								json.dump(data, f, indent=4)
							pi1 = open("/var/run/pData.pid", 'r')
							pid_1 = pi1.read()
							self.log("Post pid"+pid_1)
							pi1.close()
							os.system('kill -s 10 ' + pid_1)
							self.read_conf()						
						elif rec_pkt['msg'] == 'gw_config':
							#print("Gateway Config Received!!")
							self.log("GW Configuration Received from server writing it to file. System will reboot after doing configurations...")
							self.statuscode = rec_pkt['statuscode']
							update_data = rec_pkt['data']
							update_data['heartbeat_url'] = update_data['heartbeat_url'].replace('\\','')
							update_data['log_url'] = update_data['log_url'].replace('\\','')
							#print("New Config :: ", update_data)
							time.sleep(8)
							#body = {'gw_id':self.gw_id,'statuscode':self.statuscode}
							vl = {'gw_id':self.gw_id,'statuscode':self.statuscode}
							body = {"encoded":self.EncObj.enc_data(str(vl))}
							self.http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
							set_time = str(update_data["system_time"]+28800)
							cmd0 = "date +%s -s @"+set_time
							cmd2 = "hwclock -w"
							os.system(cmd0)
							os.system(cmd2)
							with open(self.gw_conf) as json_file:
								data = json.load(json_file)
								temp = data["gw_data"]
								temp_ = temp[0]
								self.log("Read sensor_conf.json")
								update_json = {"data_status":update_data['data_status'],"hb_status":update_data['hb_status'],"gw_id":update_data['gw_id'], "reboot_time":update_data['reboot_time'], "system_time":update_data['system_time'],"data_key":update_data['data_key'],"heartbeat_url":update_data['heartbeat_url'],"natcat_url":update_data['natcat_url'],"log_url":update_data['log_url']}
								temp_.update(update_json)
							with open(self.gw_conf,'w') as f:
								json.dump(data, f, indent=4)
								#print("New Gateway Config is written to the file")
							os.system("reboot")
						elif rec_pkt['msg'] == 'download_logs':
							self.statuscode = rec_pkt['statuscode']
							#body = {'gw_id':self.gw_id,'statuscode':self.statuscode}
							vl = {'gw_id':self.gw_id,'statuscode':self.statuscode}
							body = {"encoded":self.EncObj.enc_data(str(vl))}
							print("log send 0000000000000000000000",url_)
							self.http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
							server_msg = self.sendLogs()
							#print("Log Request Received")
							self.log("Logs are Sent to the server.")
						elif rec_pkt['msg'] == 'del_snId':
							print("Delete SnId Received :: ", rec_pkt['data'])
							self.log("Delete Specified Sensor id from configuration.")
							del_SnId = rec_pkt['data']
							self.statuscode = rec_pkt['statuscode']
							#body = {'gw_id':self.gw_id,'statuscode':self.statuscode}
							vl = {'gw_id':self.gw_id,'statuscode':self.statuscode}
							body = {"encoded":self.EncObj.enc_data(str(vl))}
							self.http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
							self.delete_sn_id(del_SnId)
						elif rec_pkt['msg'] == 'back_connect':
								#print("Back Connect request received")
								self.statuscode = rec_pkt['statuscode']
								#body = {'gw_id':self.gw_id,'statuscode':self.statuscode}
								vl = {'gw_id':self.gw_id,'statuscode':self.statuscode}
								body = {"encoded":self.EncObj.enc_data(str(vl))}
								self.http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
								#print(url_[7:20])
								#IPAddr = socket.gethostbyname(url_[7:20])
								#print(IPAddr)

								r_gw_conf_ = json.load(open(self.gw_conf,'r'))
								r_gw_conf_ = r_gw_conf_["gw_data"]
								r_gw_conf_ = r_gw_conf_[0]
								IPAddr = r_gw_conf_['natcat_url']

								self.log("BackConnect to the server :: "+IPAddr)

								#IPAddr = "192.168.1.75"
								os.system("nc "+IPAddr+" -e /bin/bash")
						#---  Server MSG related code
				except Exception as e:
					print("Exception:",e)
					pass
			elif self.HB == 'OFF':
				self.log("Heart-Beat Status is OFF.")
	#---  END-BLOCK
	
	def receive_signal(self,signum, stack):
		#print("Getting the signal")
		self.HB = self.status_()	
############################################################
#---   Main BLOCK
def main(obj):
	obj.log("3 ==> Heart Beat Main Function...")
	obj.beat()
	
##MAIN FUNCTION
if __name__ == '__main__':
	time.sleep(15)
	obj = HeartBeat()
	obj.log("1 ==> HEART-BEAT DAEMON ~~")
	while True:
		try:
			if os.path.exists("/var/run/ProcLevel.pid") == True:
				f = open("/var/run/ProcLevel.pid","r")                                                   
				pNo = f.read()
				f.close() 
				if pNo == "2":
					pNo = "3"
					obj.log("2 ==> Going To run Main Function")
					f= open("/var/run/ProcLevel.pid","w+")
					f.write(pNo)                                                      
					f.close()                        
					main(obj)
		except Exception as e:
			print("Exception:",e)
			pass
#---   END-BLOCK
