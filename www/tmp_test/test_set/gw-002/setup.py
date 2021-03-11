import os
import time
import redis


############################################################
#---  Update LOOP BLOCK
def update_f():
	print("--------------------------------------------------")
	per_cmd   = "chmod 777 /www/tmp_test/test_set/gw-002/web/_netw/receive"
	rmf_cmd   = "rm /www/tmp_test/gw-002.zip"
	os.system(per_cmd)
	os.system(rmf_cmd)
	#conn.flushall()
	#os.system("reboot")
			
#---  END-BLOCK


############################################################
##MAIN FUNCTION
if __name__ == '__main__':
	update_f()
#---   END-BLOCK
