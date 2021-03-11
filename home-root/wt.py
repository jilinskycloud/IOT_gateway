import subprocess


state = subprocess.Popen("iw wlan0 info", shell=True, stdout=subprocess.PIPE).stdout
state =  state.read().decode().split('\n')[5].split(' ')[1]
print(state)


#state =  state.read()
#state = state.decode()
#state = state.split('\n')
#state = state[5].split(' ')
#print(state[1])
