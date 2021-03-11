import os
import httplib2
import urllib
import time
import subprocess
import redis
import json
import signal
import socket
from _includes.EncDec import EncDec
import base64

class sendTempDist:
  def __init__(self):
    self.Xcount = 0
    self.EncObj = EncDec()
    with open("/www/wpScripts/_configs/path_conf.json") as json_file:
      _paths = json.load(json_file)
    self.log_path = _paths['p_sendTemoDist_log']
    self.gw_conf = _paths['gw_conf_']
    self.sensor_conf = _paths['sensor_conf_']
    self.content = ''
    self.st_pid = '/var/run/pData.pid'
    self.post_data_status = ''
    self.conn  = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True, password="LoRaDB")
    self.http = httplib2.Http(".cache",  disable_ssl_certificate_validation=True)
    signal.signal(signal.SIGUSR1, self.receive_signal)
    pidis = str(os.getpid())
    #print('SendTemp.py process ID ==> ',pidis)
    self.log('SendTempDist.py PID IS ==> '+pidis)
    f= open(self.st_pid,"w+")
    f.write(pidis)
    f.close()
    proc = subprocess.Popen(["hostname"], stdout=subprocess.PIPE, shell=True)
    (self.gw_id, err1) = proc.communicate()
    self.gw_id = self.gw_id.decode('utf-8')
    self.gw_id = self.gw_id.strip()
    self.r_sensor_conf = ''
    self.status_()
    
  ############################################################
  #---  Log BLOCK
  def log(self,log_str):
      #print("Log Function... ",self.Xcount)
      log_str = str(log_str)+" \n"                                                                                                   
      self.Xcount = self.Xcount + 1                                                                                                              
      if os.path.exists(self.log_path) == False:                                                                                             
          #print("File not exist CEATING IT")                                                                                         
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
  #---  Sensor File Read Block
  def read_sensor_conf(self):
    input_file = open(self.sensor_conf)
    self.r_sensor_conf = json.load(input_file)
    self.r_sensor_conf = self.r_sensor_conf["sensors_data"]
  #---  END-BLOCK 

  ############################################################
  #---  PostData Status Block
  def status_(self):
    r_gw_conf = json.load(open(self.gw_conf,'r'))
    r_gw_conf = r_gw_conf["gw_data"]
    r_gw_conf = r_gw_conf[0]
    self.read_sensor_conf()
    if r_gw_conf['data_status'] == 1:
      self.post_data_status = "ON"
      #print("Post Data Status is ON")
      self.log("Post Data Status is ON")
    else:
      self.post_data_status = "OFF"
      #print("Post Data Status is OFF")
      self.log("Post Data Status is OFF")
    return self.post_data_status
    
  #---  END-BLOCK 

  ############################################################
  #---  Read redis Block
  def get_from_redis(self,sn_id):
    if self.conn.hexists("sensor_data",sn_id) == 1:
      return self.conn.hget("sensor_data",sn_id)
    else:
      #print(sn_id, "-ID doesn't Exists!!!!")
      return "NULL"
  #---  END-BLOCK 

  ############################################################
  #---  Read Temp redis Block
  def set_last_send_time_from_redis(self,sn_id):
    last_send = {sn_id:time.time()} #0 index is sensor id and index 1 is temperature
    self.conn.hmset("last_send_time",last_send)
    return 0
  #---  END-BLOCK 

  ############################################################
  #---  Read Last Send Time redis Block
  def get_last_send_time_from_redis(self,sn_id):
    if self.conn.hexists("last_send_time",sn_id) == 1:
      #print("Get Last Send time")
      return self.conn.hget("last_send_time",sn_id)
    else:
      last_send = {sn_id:0} 
      self.conn.hmset("last_send_time",last_send)
      return self.conn.hget("last_send_time",sn_id)
  #---  END-BLOCK 

  ############################################################
  #---  Post Data Block
  def post_Data(self,):
    self.log("4 ==> PostData Function...")
    all_keys = list(self.conn.hgetall('sensor_data').keys())
    if len(all_keys) != 0:
      self.conn.hdel('sensor_data', *all_keys)
    self.read_sensor_conf()
    while(1):
      try:
        if self.post_data_status == "ON":		
          for SN in self.r_sensor_conf:	
            if SN["ST"] == "distance":
              last_time = self.get_last_send_time_from_redis(SN["sn_id"])
              s_t  = SN["ST"]
              sn_id = SN["sn_id"]
              url_ = SN["data_api_address"]
              if (float(time.time()) - float(last_time) > float(SN["data_interval"])):
                dist = self.get_from_redis(sn_id)
                if dist != "NULL": 
                  #print("tmp|time:: ",temp)
                  self.log("dist|time:: "+dist)
                  tr = dist.split("|")
                  dist = tr[0]
                  max = tr[1]
                  min = tr[2]
                  sniff_time = tr[3]
                  #print("cTime:", int(time.time()), "sniff_time: ",int(sniff_time))
                  diff_time = int(time.time()) - int(sniff_time) 
                  #print("Difference is  ::",diff_time)
                  if diff_time > 1200:
                    #print("No Latest Reading----")
                    self.log("No Latest Reading!!")
                  else:
                    #print("Service Type IS :: ", SN["ST"])
                    #s = '{\"s_time\":\"'+time.ctime()+'\", \"gw_id\":\"'+self.gw_id+'\", \"sn_id\":\"'+sn_id+'\", \"ST\":\"'+s_t+'\", \"temp\":\"'+dist+'\",  \"max\":\"'+max+'\",  \"min\":\"'+min+'\"}'
                    #body = {'post_data':s}
                    s = {"s_time":time.ctime(),"gw_id":self.gw_id,"sn_id":sn_id,"ST":s_t,"temp":dist,"max":max,"min":min}			   
                    body = {'encoded':s}
                    print("Sending Distance data to server data is:",body)
                    self.content = self.http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
                    #self.content = self.content.decode("utf-8")
                    self.content = eval(base64.b64decode(self.EncObj.dec_data(eval(self.content.decode("utf-8")))).decode("utf-8"))
                    print("Distance Service :", self.content)
                    self.set_last_send_time_from_redis(SN["sn_id"])
                    #print("Received From the server ==>", self.content)
                ########### Distance Code ###########
            elif SN["ST"] == "temperature":			
              temp = self.get_from_redis(SN["sn_id"])
              last_time = self.get_last_send_time_from_redis(SN["sn_id"])
              s_t  = SN["ST"]
              url_ = SN["data_api_address"]
              sn_id = SN["sn_id"]
              if float(time.time()) - float(last_time) > float(SN["data_interval"]):
                if temp != "NULL": 
                  #print("tmp|time:: ",temp)
                  self.log("tmp|time:: "+temp)
                  tr = temp.split("|")
                  temp = tr[0]
                  sniff_time = tr[1]
                  diff_time = int(time.time()) - int(sniff_time) 
                  #print("Difference is  ::",diff_time)
                  if diff_time > 1200:
                    #print("No Latest Reading")
                    self.log("No Latest Reading!!")
                  else:
                    #print("Service Type is:: ", SN["ST"])
                    #s = '{\"s_time\":\"'+time.ctime()+'\", \"gw_id\":\"'+self.gw_id+'\", \"sn_id\":\"'+sn_id+'\", \"ST\":\"'+s_t+'\", \"temp\":\"'+temp[:5]+'\"}' 
                    #print("Sent Packet",s)
                    #body = {'post_data':s}
                    s = {"s_time":time.ctime(), "gw_id":self.gw_id, "sn_id":sn_id, "ST":s_t, "temp":temp[:5]}
                    print("Sent Packet",s)
                    s = self.EncObj.enc_data(str(s))
                    body = {'encoded':s}
                    print("Sending Temperature data to server data is:",body)
                    self.http = httplib2.Http(".cache",  disable_ssl_certificate_validation=True)
                    print("This is the Sending URL :: ", url_)
                    self.content = self.http.request(url_, method="POST", headers={'Content-type': 'application/x-www-form-urlencoded'}, body=urllib.parse.urlencode(body) )[1]
                    print("Tatti :: ", self.content)
                    #self.content = self.content.decode("utf-8")
                    self.content = eval(base64.b64decode(self.EncObj.dec_data(eval(self.content.decode("utf-8")))).decode("utf-8"))
                    last_send = time.ctime()
                    print("Post-Daemon ==> This is server MSG", self.content)
                    self.conn.hset("ping_stt", "sd_stt", rec_pkt['code'])
                    print("Packet Sent")
                    self.log("Data Sent to the server.")
                    self.set_last_send_time_from_redis(SN["sn_id"])
              else:
                tmpx = 0
            elif SN["ST"] == "--":
        	    #print("ST is Empty!!!!!")
              self.log(("ST is Empty!! ____"))
        else:
          #print("Send Data is OFF")
          self.log("Send Data is OFF")
          pass
      except Exception as e:
        print("Exception:",e)
        #pass
  #---  END-BLOCK
  def receive_signal(self,signum, stack):
    #print("Getting signal!!")
    self.post_data_status = self.status_()  
  #---  END-BLOCK

############################################################
#---  Main Function Block
def main(obj):
  obj.log("3 ==> sendTempDist Main Function.")
  obj.post_Data()

if __name__ == '__main__':
  time.sleep(25)
  obj = sendTempDist()
  obj.log("1 ==> ~~ POST DATA DAEMON ~~")
  while True:
    try:
      if os.path.exists("/var/run/ProcLevel.pid") == True:
        f = open("/var/run/ProcLevel.pid","r")
        pNo = f.read()
        f.close()
        if pNo == "3":
          pNo = "4"
          obj.log("2 ==> Going To Run Main Function...")
          f = open("/var/run/ProcLevel.pid","w+")
          f.write(pNo)
          f.close()
          main(obj)
    except Exception as e:
      print("Exception:",e)
      #pass
#---  END-BLOCK