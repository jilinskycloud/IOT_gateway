from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import base64


class EncDec:
	def __init__(self):
		self.key = b'al\x83j\xd7M\xca*3\x11\xc4\x8e\x7f\xf0\xbf\x1a' #get_random_bytes(16)
	
	def bs64(self, vl):
		return str(base64.b64encode(vl), 'utf-8')
		#return base64.b64encode(vl)

		
	def enc_data(self, a):
		a = str.encode(a)
		self.cipher = AES.new(self.key, AES.MODE_EAX)
		msg = {"nounce":self.bs64(self.cipher.nonce),"cipher":self.bs64(self.cipher.encrypt(a))}
		return msg
		
	def dec_data(self, data):
		dd = data    #.split(',')
		nonce = base64.b64decode(dd['nounce'])
		ciphertext = base64.b64decode(dd['cipher'])
		cipher = AES.new(self.key, AES.MODE_EAX, nonce)
		plaintext = cipher.decrypt(ciphertext)
		plaintext = plaintext.decode("utf-8")
		return plaintext


if __name__ == '__main__':
	obj = EncDec()
	print(obj.dec_data("abc"))