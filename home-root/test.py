import re
import os
abc = []
with open('wpa_supplicant_ap.conf') as f:
  text = f.read()
  abc = text.split("\n")
  print(abc[1].replace('     ssid="','').replace('"',''))
  print(abc[6].replace('     psk="','').replace('"',''))


with open('wpa_supplicant_ap.conf', 'rw') as f:
  a = f.read() 
  a = a.replace("Tain-WangGuan-001","jdhfkjshdkf").replace("11223344","12345678")
  f.write(a)

