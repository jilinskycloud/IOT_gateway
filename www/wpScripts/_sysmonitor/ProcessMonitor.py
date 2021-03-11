import os
import subprocess
import time
import psutil
import redis
import json

class ProcessMon:
  def __init__(self):
    with open("/www/wpScripts/_configs/path_conf.json") as json_file:
      _paths = json.load(json_file)
    self.pro_list = _paths['proMon_f']
    self.log_path = _paths['p_processmonitor_log']
    self.sleep_time = 5 #10*60  # 10 minutes
    self.conn = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True, password="LoRaDB")
    self.Xcount = 0
    self.Ycount = 0

  ############################################################
  #---  LOG BLOCK
  def log(self,log_str):                                                                                                                  	
      #print("Log Function...",self.Xcount)
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
  #---  CHECK PID's BLOCK
  def check_process(self):
    x = 0
    for proc in psutil.process_iter():
      if proc.name() == "python3":
        if proc.cmdline()[1] in self.pro_list:
          x = x+1
    return x
  #---  END-BLOCK

  ############################################################
  #---  Main Loop BLOCK
  def monitorIt(self):
  	self.log("4 ==> monitorIt Funciton...")
  	while(1):
  		try:
  			stt = self.conn.hgetall("ping_stt")
  			time.sleep(self.sleep_time)
  			#print("Number of Processes Running :: ",self.check_process())
  			self.log("Number of Processes Running :: "+str(self.check_process()))
  			if self.check_process() < 9:
  				self.Ycount = self.Ycount + 1
  				print("Some processes are not running and Reboot (Ycount) is ::", self.Ycount)
  				self.log("Some processes are not running and Reboot (Ycount) is ::"+str(self.Ycount))
  			if self.Ycount > 10:
  				self.Ycount = 0
  				#print("There is a process who got stopped Lets reboot the system!! bye bye...")
  				os.system("reboot")
  			#print(int(time.time()), ">", stt['hb_stt'].split('|')[1])
  			sr = int(time.time()) - int(stt['hb_stt'].split('|')[1])
  			if sr > 600:
  				self.Ycount = self.Ycount + 1
  		except Exception as e:
  			print("Exception:",e)
  			pass
  #---  END-BLOCK

def main(obj):
  obj.log("3 ==> ProcessMonitor Main Function...")
  obj.monitorIt()

############################################################
#---  This is Main Function
if  __name__  ==  '__main__' :
  obj = ProcessMon()
  obj.log("1 ==> ~~PROCESS MONITOR DAEMON ~~")
  time.sleep(60)
  obj.log("2 ==> Going to run Main Function")
  main(obj)
#---  END-BLOCK

