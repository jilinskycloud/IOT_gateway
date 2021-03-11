import time
import json
import os
import signal

class Reboot:
	def __init__(self):
		with open("/www/wpScripts/_configs/path_conf.json") as json_file:
			_paths = json.load(json_file)
		self.gw_conf = _paths['gw_conf_']
		self.Xcount = 0
		self.log_path = _paths['p_reboot_log']
		self.trigger = ''
		self.file_change_pid = "/var/run/reboot.pid"

	############################################################
	#---  Post Data Block
	def log(self,log_str):                                                                              
	    #print("Log Function...",Xcount)
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
	#---  Update Conf BLOCK
	def read_conf(self):
		r_gw_conf = []
		input_file = open(self.gw_conf)
		r_gw_conf = json.load(input_file)
		r_gw_conf = r_gw_conf["gw_data"]
		r_gw_conf = r_gw_conf[0]
		input_file.close()
		self.log("Here we gonna test reboot!!")
		self.trigger = r_gw_conf['reboot_time']
	#---  END-BLOCK 

	############################################################
	#---  Reboot BLOCK
	def simulate_reboot(self):
		self.log("4 ==> simulate_reboot Function...")
		self.read_conf()
		while(1):
			try:
				time.sleep(3)
				tm = time.strftime('%X')
				#print("C-Time is", tm[:8], " and reboot time is ", self.trigger[:5])
				self.log("Current Time is "+tm[:8]+" and reboot time is "+ self.trigger[:5])
				if(tm[:5] == self.trigger[:5]):
					time.sleep(59)
					#print("Reboot the System!")
					self.log("Its a Scheduled Reboot. Lets Reboot and have a little rest :)")
					os.system("reboot")
				time.sleep(58)
			except Exception as e:
				print("Exception:",e)
				pass
	#---  END-BLOCK 

############################################################
#---  Main BLOCK 
def main(obj):
	obj.log("3 ==> reboot Main Funciton...")
	obj.simulate_reboot()
 
if  __name__  ==  '__main__' :
	obj = Reboot()
	obj.log("1 ==> ~~REBOOT DAEMON ~~")
	obj.log("2 ==> Going to run Main Function")
	main(obj)
#---  END-BLOCK 
  

  

