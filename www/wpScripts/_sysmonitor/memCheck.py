import subprocess
import os
import time
import json

class MemCheck:
  def __init__(self):
    with open("/www/wpScripts/_configs/path_conf.json") as json_file:
      _paths = json.load(json_file)
    self.log_path = _paths['p_memCheck_log']
    self.Xcount = 0                                          
 
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
  #--- MEM-CHECK BLOCK 
  def memcheck(self):
    self.log("4 ==> memcheck Function...")
    cmd = "free -m|grep Mem"
    while(1):
      try:  
        rzlt = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
        (rzlt, err1) = rzlt.communicate()
        rzlt = rzlt.decode('utf-8')
        rzlt = '-'.join(rzlt.split())
        rzlt = rzlt.split("-")[3]
        if int(rzlt) < 40:
          #print("Need to Flush The Buffer!!")
          self.log("Need to Flush Buffer bcz Mem is :"+rzlt)
          os.system("echo 3 > /proc/sys/vm/drop_caches")
        time.sleep(3600)
      except Exception as e:
        print("Exception:",e)
        pass
  #---  END-BLOCK

def main(obj):
  obj.log("3 ==> memcheck Main Function...")
  obj.memcheck()
############################################################          
#--- MAIN BLOCK 
if __name__ == '__main__':
  obj = MemCheck()
  obj.log("1 ==> ~~MEM-CHECK DAEMON ~~")
  time.sleep(60)
  obj.log("2 ==> Going  to run Main Function.")
  main(obj) 
#---   END-BLOCK



