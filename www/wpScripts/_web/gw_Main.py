#/usr/bin/python3

from flask import Flask
from flask import escape
from flask import url_for
from flask import request
from flask import render_template
from flask import flash
from flask import redirect
from flask import session
from flask import jsonify
from jinja2 import Template
import datetime
import psutil
import time
import json
import sqlite3
import os
import redis 
import subprocess                                                                                         
  
#			GLOBAL VARIABLES BLOCK
###########################################################
global Xcount
global sensor_conf_
global gw_conf_
global p_flask_log
global _paths  

with open("/www/wpScripts/_configs/path_conf.json") as json_file:
  _paths = json.load(json_file)
#print("ALL PATHS :: ",_paths)
p_flask_log = _paths['p_flask_log']

r = redis.StrictRedis(host='localhost', port=6370, db=0, charset="utf-8", decode_responses=True, password="LoRaDB")
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
sensor_conf_ = _paths['sensor_conf_']
gw_conf_ = _paths['gw_conf_']
Xcount = 0 
conn = sqlite3.connect(_paths['sqlitedb'])
conn.close()

#			Jinja2 Filter Functions
###########################################################
def tFormate(tstamp):
	return datetime.datetime.fromtimestamp(float(tstamp)).isoformat()
app.jinja_env.filters['tFormate'] = tFormate
###

#			This is Log Function
###########################################################
def log(log_str):                           
    global Xcount                                   
    global p_flask_log  
    #print("Log Function...........:: ",Xcount)                     
    log_str = str(log_str)+" \n"               
    Xcount = Xcount+1 
    if os.path.exists(p_flask_log) == False:
        #print("Log File not exist CEATING IT")
        open(p_flask_log, "w").close()            
    with open(p_flask_log, 'a') as outfile:                
        outfile.write(log_str)                   
    if Xcount > 500:
        cmd_rm = "rm "+p_flask_log                 
        os.system(cmd_rm)                                       
        Xcount = 0                                         
    return
###

#			This is Get Command Function
###########################################################
'''
@app.route('/getcmd', methods=['GET', 'POST'])
def getcmd():
	if request.method == 'POST':
		log("Get Command Function.......")
		input_json = request.get_json(force=True)
		os.system(input_json)
	dictToReturn = {'answer':42}
	return jsonify(dictToReturn)
'''
###

#			This is Scan Wifi Function
###########################################################
@app.route('/scanWifi', methods=['GET', 'POST'])
def scanWifi():
	if 'username' in session:
		if request.method == 'POST':
			log("Scan Wifi Function..")
			os.system("ifconfig wlan0 down")
			time.sleep(4)
			os.system("ifconfig wlan0 up")
			time.sleep(4)
			cmd = 'iwlist wlan0 scan|grep ESSID'
			proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
			(ssids, err1) = proc.communicate()
			ssids = ssids.decode('utf-8').replace(' ','').replace('\n',',').replace('ESSID:','').replace('"','')
			#print("SSIDS : ", ssids)
		return ssids
	else:
		return redirect(url_for('login'))
###

#			This is Connect Wifi Function
###########################################################
@app.route('/connectWifi', methods=['GET', 'POST'])
def connectWifi():
	if 'username' in session:
		if request.method == 'POST':
			log("Connecting to Wifi")
			ssid = request.form["ssid"]
			password = request.form["password"]
			#print("ssid:: ",ssid," pass:: ",password)
			os.system("killall wpa_supplicant")
			cmd1 = "wpa_passphrase "+ ssid +" "+ password +"| tee /www/wpScripts/_configs/wpa_supplicant.conf"
			os.system(cmd1)
			time.sleep(4)
			cmd2 = "wpa_supplicant -D wext -B -i wlan0 -c /www/wpScripts/_configs/wpa_supplicant.conf"
			os.system(cmd2)
			time.sleep(4)
			cmd3 = "udhcpc -b -i wlan0 -R"
			os.system(cmd3)
			os.system('/etc/init.d/networking restart')
		return redirect(url_for('network'))
	else:
		return redirect(url_for('login'))
###

#			This is LoRa Reset Function
###########################################################
@app.route('/resetLora', methods=['GET', 'POST'])
def resetLora():
	if 'username' in session:
		reset_lora = request.form['reset_lora']
		if request.method == 'POST':
			log("Switch ON/OFF BLE : "+reset_lora)
			reset_lora = request.form['reset_lora']
			os.system("echo 1 > /sys/class/leds/rst_ble62/brightness")
			time.sleep(2)
			os.system("echo 0 > /sys/class/leds/rst_ble62/brightness")
			return redirect(url_for('settings'))
	else:
		return redirect(url_for('login'))
###

#			This is Reboot Function
###########################################################
@app.route('/reboot')
def reboot():
	log("System Reboot Function.")
	os.system("reboot")
	ipis = cm("ifconfig eth0| egrep -o '([[:digit:]]{1,3}\.){3}[[:digit:]]{1,3}'")
	ipis = ipis.split("\n")
	return "<div style='background-color:red; background-color: #e4e0e0; margin: 0px; width: 700px; text-align: center; padding: 15px; color: black; margin-left: auto; margin-right: auto;'>Device Going to Reboot! To Access Web Please <a href='http://"+ipis[0]+"/'>Click Here</a> After 2 minutes...</div>"
###

#			These is MYSQL  Functions
###########################################################
@app.route('/delProfile/<ids>')
def delProfile(ids=None):
	conn = sqlite3.connect(_paths['sqlitedb'])
	log("Delete Admin entry :: "+ids)
	f = conn.execute("DELETE FROM login where id=?", (ids,))
	conn.commit()
	conn.close()
	flash("Deleted successfully")
	return redirect(url_for('settings'))
###

#=============================================================
#=====================WEB-PAGE FUNCTIONS======================
#=============================================================

#			This is an Index  Function
###########################################################
@app.route('/')
@app.route('/index/')
@app.route('/index')
def index():
	if 'username' in session:
		log("Index Page Function...")
		return redirect(url_for('dashboard'))
	return redirect(url_for('login'))
###

#			This is Language  Function
###########################################################
@app.route('/lng', methods=['GET', 'POST'])
def lng():
	if 'username' in session:
		if request.method == 'POST':
			session['lng'] = request.form["lng"]
			print("This is the Language:::", session['lng'])
			return redirect(url_for('dashboard'))
	else:
		return redirect(url_for('index'))
###

#			This is Dashboard  Function
###########################################################
@app.route('/dashboard')
def dashboard():
	if 'username' in session:
		log("Dashboard Function...")
		global sensor_conf_
		sn_liststt = r.hgetall('sensor_stt')
		sn_list = {}
		with open(sensor_conf_) as f:
			data = json.load(f)
			data = data['sensors_data']
			for x in range(len(data)):
				sn_list[x] = data[x]['sn_id']
		sn_stt = {}
		print(sn_liststt)
		for key1, value in sn_list.items():
			f1=0
			for key2 in sn_liststt:
				if value == key2:
					sn_stt.update({value:'on'})
					f1 = 1
					break
			if f1==0:
				sn_stt.update({value:'off'})
		u_name = escape(session['username'])
		log(session.get('device1'))
		cmd = "hostname"                   
		proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
		(gw_id, err1) = proc.communicate()       
		gw_id = gw_id.decode('utf-8')
		gw_id = gw_id.strip()   
		data = {}
		data['serial'] = gw_id
		data['cpu'] = psutil.cpu_percent()
		data['stats'] = psutil.cpu_stats()
		data['cpu_freq'] = psutil.cpu_freq()
		data['cpu_load'] = psutil.getloadavg()
		data['ttl_memo'] = round(psutil.virtual_memory().total/1048576)
		data['ttl_memo_used'] = round(psutil.virtual_memory().used/1048576)
		data['ttl_memo_avai'] = round(psutil.virtual_memory().available/1048576)
		data['swp_memo'] = psutil.swap_memory()
		data['hostname'] =cm("hostname")
		data['routeM'] = 'TC-001'
		data['FirmV'] = 'v1.0.00_TempSniffer_TainCloud_r001'
		data['lTime'] = cm('date')
		data['runTime'] = cm('uptime')
		data['network'] = cm("ifconfig eth0| egrep -o '([[:digit:]]{1,3}\.){3}[[:digit:]]{1,3}'")
		data['mount'] = psutil.disk_partitions(all=False)
		data['disk_io_count'] = psutil.disk_io_counters(perdisk=False, nowrap=True)
		data['net_io_count'] = psutil.net_io_counters(pernic=False, nowrap=True)
		data['nic_addr'] = psutil.net_if_addrs()
		data['tmp'] = psutil.sensors_temperatures(fahrenheit=False)
		data['boot_time'] = psutil.boot_time()
		data['c_user'] = psutil.users()
		data['reload'] = time.time()
		_tempD_log = r.lrange("temp_logs",0,-1)
		_tempD_logY = [i.split('|')[0] for i in _tempD_log]
		_tempD_logX = [float(i.split('|')[1]) for i in _tempD_log]
		_distD_log = r.lrange("dist_logs",0,-1)
		cmd = "cat /var/lib/misc/dnsmasq.leases"
		proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
		(dhcp_lease, err1) = proc.communicate()
		dhcp_lease = dhcp_lease.decode('utf-8')
		#print("This is lease",dhcp_lease)
		#print("This is Lease Type ",type(dhcp_lease))
		dhcp_lease = dhcp_lease.split('\n')
		dhcp_lease = list(filter(None,dhcp_lease))
		dhcp_len = len(dhcp_lease)
		if session['lng'] == 'cn':
			return render_template('cn/dashboard.html', data=data, tempY=_tempD_logY, tempX=_tempD_logX, dist=_distD_log, sn_stt=sn_stt, dhcp_lease=dhcp_lease, dhcp_len=dhcp_len)
		else:
			return render_template('en/dashboard.html', data=data, tempY=_tempD_logY, tempX=_tempD_logX, dist=_distD_log, sn_stt=sn_stt, dhcp_lease=dhcp_lease, dhcp_len=dhcp_len)
	else:
		return redirect(url_for('login'))
###

#			This is get command from Dashboard  Function
###########################################################
def cm(dt):
	log("Inner CMD Function......Dashboard Page")
	klog = subprocess.Popen(dt, shell=True, stdout=subprocess.PIPE).stdout
	klog1 =  klog.read()
	cm_ret = klog1.decode()
	return cm_ret
###

#			This is Sensor config Post Function
###########################################################
@app.route('/sensor_conf', methods=['GET', 'POST'])
def sensor_conf():
	if 'username' in session:
		if request.method == 'POST':
			result = request.form["json_data"]
			with open(sensor_conf_, 'w') as json_file:
				json_file.write(result)
			flash("Sensor Config is Updated")
			pi1 = open("/var/run/pData.pid", 'r')
			pid = pi1.read()
			log("Killing pid is (sensor_conf)"+pid)
			pi1.close()
			os.system('kill -s 10 ' + pid)
		return redirect(url_for('settings'))
	else:
		return redirect(url_for('login'))		
###

#			Theis is GW config Post Function
###########################################################
@app.route('/gw_conf', methods=['GET', 'POST'])
def gw_conf():
	if 'username' in session:
		if request.method == 'POST':
			result = request.form["json_data"]
			with open(gw_conf_, 'w') as json_file:
				json_file.write(result)
			flash("GW Config is Updated")
		return redirect(url_for('settings'))
	else:
		return redirect(url_for('login'))	
###

#			This is Console Log Function
###########################################################
@app.route('/console_logs')
def console_logs():
	global _paths
	if 'username' in session:
		log("Console Logs Function...")
		try:
			klog = subprocess.Popen("dmesg", shell=True, stdout=subprocess.PIPE).stdout
			klog1 =  klog.read()
			pc = klog1.decode()
			flask = subprocess.Popen("cat "+_paths['p_flask_log'], shell=True, stdout=subprocess.PIPE).stdout
			flask =  flask.read()
			flask_log = flask.decode()
			hb = subprocess.Popen("cat "+_paths['p_hb_log'], shell=True, stdout=subprocess.PIPE).stdout
			hb =  hb.read()
			hb_log = hb.decode()
			_postD = subprocess.Popen("cat "+_paths['p_sendTemoDist_log'], shell=True, stdout=subprocess.PIPE).stdout
			_postD =  _postD.read()
			_postD_log = _postD.decode()
			_reb = subprocess.Popen("cat "+_paths['p_reboot_log'], shell=True, stdout=subprocess.PIPE).stdout
			_reb =  _reb.read()
			_reb_log = _reb.decode()
			_pro = subprocess.Popen("cat "+_paths['p_processmonitor_log'], shell=True, stdout=subprocess.PIPE).stdout
			_pro =  _pro.read()
			_pro_log = _pro.decode()
			_dist = subprocess.Popen("cat "+_paths['p_readdist_log'], shell=True, stdout=subprocess.PIPE).stdout
			_dist =  _dist.read()
			_dist_log = _dist.decode()
			_temp = subprocess.Popen("cat "+_paths['p_readlora_log'], shell=True, stdout=subprocess.PIPE).stdout
			_temp =  _temp.read()
			_temp_log = _temp.decode()
			_update = subprocess.Popen("cat "+_paths['p_update_log'], shell=True, stdout=subprocess.PIPE).stdout
			_update =  _update.read()
			_update_log = _update.decode()
			_tempR_log = r.lrange("temp_logs",0,-1)
			_distR_log = r.lrange("dist_logs",0,-1)
			if session['lng'] == 'cn':
				return render_template('cn/console-logs.html', data=pc, flask_log=flask_log, hb_log=hb_log, _postD_log=_postD_log, _reb_log=_reb_log, _pro_log=_pro_log, _temp_log=_temp_log, _dist_log=_dist_log, _tempR_log=_tempR_log, _distR_log=_distR_log, _update_log=_update_log)
			else:
				return render_template('en/console-logs.html', data=pc, flask_log=flask_log, hb_log=hb_log, _postD_log=_postD_log, _reb_log=_reb_log, _pro_log=_pro_log, _temp_log=_temp_log, _dist_log=_dist_log, _tempR_log=_tempR_log, _distR_log=_distR_log, _update_log=_update_log)
		except Exception as e:
			print("Exception : ",e)
			pass
	else:
		return redirect(url_for('login'))
###

#			This is Network Interface Function
###########################################################
@app.route('/network', methods=['GET', 'POST'])
def network():
	if 'username' in session:
		if request.method == 'POST':
			if request.form["type"] == "client12":
				result = request.form["net_data"]
				result.replace('\r','')
				log(result)
				with open("/etc/network/interfaces", "w") as f:
					f.write(result.replace('\r\n', os.linesep))
				flash("network File Updated")
			elif request.form['type'] == "ap":
				o_ap_ssid = request.form['o_ap_ssid']
				o_ap_pass = request.form['o_ap_password']
				n_ap_ssid = request.form['n_ap_ssid']
				n_ap_pass = request.form['n_ap_password']
				f = open('/www/wpScripts/_configs/wpa_supplicant.conf', 'r')
				rd = f.read()
				f.close()
				f = open('/www/wpScripts/_configs/wpa_supplicant.conf', 'w')
				a = rd.replace(o_ap_ssid,n_ap_ssid).replace(o_ap_pass,n_ap_pass)
				f.write(a)
				f.close()
				os.system("killall wpa_supplicant")
				time.sleep(5)
				subprocess.Popen("wpa_supplicant -B -Dnl80211 -iwlan0 -c /home/root/wpa_supplicant_ap.conf", shell=True, stdout=subprocess.PIPE).stdout
		net = subprocess.Popen("cat /etc/network/interfaces", shell=True, stdout=subprocess.PIPE).stdout
		net =  net.read()
		net = net.decode()
		abc = []
		with open(_paths['ap_config']) as f:
			text = f.read()
			abc = text.split("\n")
			abc[1] = abc[1].replace('     ssid="','').replace('"','')
			abc[6] = abc[6].replace('     psk="','').replace('"','')
			#print(abc[6])
			state = subprocess.Popen("iw wlan0 info", shell=True, stdout=subprocess.PIPE).stdout
			state =  state.read().decode().split('\n')#[5].split(' ')[1]
			if len(state) == 8:
				state = state[5].split(' ')[1]
			elif len(state) == 7:
				state = state[4].split(' ')[1]
		if session['lng'] == 'cn':
			return render_template('cn/network.html', net=net, ssid=abc[1], password=abc[6], state=state)
		else:
			return render_template('en/network.html', net=net, ssid=abc[1], password=abc[6], state=state)
	else:
		return redirect(url_for('login'))
###	

#			Theis is Settings Function
###########################################################
@app.route('/settings', methods=['GET', 'POST'])
def settings():
	global sensor_conf_
	global gw_conf_
	error = None
	data = []
	rec=[]
	if 'username' in session:
		if request.method == 'POST':
			log("Setting Function (in POST)")
			data.append(request.form['name'])
			data.append(request.form['pass'])
			log(data)
			conn = sqlite3.connect(_paths['sqlitedb'])
			conn.execute("INSERT INTO login (username,password) VALUES (?,?)",(data[0], data[1]) )
			conn.commit()
			conn.close()
			msg = "Record successfully added"
			flash("Login Details Added successfully")
		conn = sqlite3.connect(_paths['sqlitedb'])
		f = conn.execute("SELECT * FROM login")
		rec = f.fetchall()
		conn.close()
		stt_lora = os.popen('cat /sys/class/leds/rst_lora118/brightness').read()
		log("BLE Reset State:: "+stt_lora)
		if int(stt_lora) == 1 or int(stt_lora) == 255:
			stt_lora = "ON"
		else:
			stt_lora = "OFF"
		with open(gw_conf_) as json_file:  
		  conn_status = json.load(json_file)           
		  conn_status = conn_status["gw_data"]    
		  conn_status = conn_status[0]
		f = open(sensor_conf_,"r")
		sn_conf_d = f.read()
		f = open(gw_conf_,"r")
		gw_conf_d = f.read()
		if session['lng'] == 'cn':
			return render_template('cn/settings.html', error=error, data=data, rec=rec, chk=conn_status, stt_lora=stt_lora, sn_conf_d=sn_conf_d, gw_conf_d=gw_conf_d)
		else:
			return render_template('en/settings.html', error=error, data=data, rec=rec, chk=conn_status, stt_lora=stt_lora, sn_conf_d=sn_conf_d, gw_conf_d=gw_conf_d)
	else:
		return redirect(url_for('login'))
###

#			This is HB/POST en/dis Function
###########################################################
@app.route('/connect', methods=['GET','POST'])
def connect():
	if 'username' in session:
		if request.method == 'POST':
			result = request.form.to_dict()
			log("result"+result)
			with open("/www/web/config123.text", "w") as f:
				json.dump(result, f, indent=4)
				flash("Network Configuration Updated")
			#print(os.system("cat /var/run/hBeat.pid"))
			log(os.system("cat /var/run/hBeat.pid"))
			pi = open("/var/run/hBeat.pid", 'r')
			pid_ = pi.read()
			pi.close()
			os.system('kill -s 10 ' + pid_)
			pi1 = open("/var/run/pData.pid", 'r')
			pid_1 = pi1.read()
			log("this is the post pid"+pid_1)
			pi1.close()
			os.system('kill -s 10 ' + pid_1)
		return redirect(url_for('settings'))
	else:
		return redirect(url_for('login'))
###

#			This is Login Function
###########################################################
@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'POST':
		u_name = request.form['username']
		u_pass = request.form['password']
		flag = 0
		conn = sqlite3.connect(_paths['sqlitedb'])
		f = conn.execute("SELECT * FROM login WHERE username=? and password=?", (u_name, u_pass))
		v = f.fetchall()
		if(len(v) > 0):
			flag = 0
		else:
			flag = -1
		conn.close()
		if(flag == -1):
			error = 'Invalid Credentials. Please try again.'
		else:
			session['username'] = request.form['username']
			session['lng'] = 'en'
			flash('Successfully logged in')
			log("Successfully logged in")
			return redirect(url_for('index'))
	return render_template('en/login.html', error=error)
###

#			This is Logout Function
###########################################################
@app.route('/logout')
def logout():
	session.pop('username', None)
	return redirect(url_for('index'))
###

#			This is Main Function
###########################################################
if  __name__  ==  '__main__' : 
	log("1 ==> ~~ FLASK WEB DAEMON ~~")
	if os.path.exists("/var/process_logs/flask_daemon.log") == False:                   
		#print("Log File not exist CEATING IT")
		log("2.1 ==> Log File does not exist Creating It.")
		open("/var/process_logs/flask_daemon.log", "w").close() 
	else:
		#print("log file exists")
		log("2.2 ==> Log file exists")
	#time.sleep(60)	
	app.run(host='0.0.0.0', port=80, threaded = True, debug = True)# ssl_context='adhoc') #Ssl_context = Context ,
