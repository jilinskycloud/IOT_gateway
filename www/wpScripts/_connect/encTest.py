from _includes.EncDec import EncDec

x = {'gw_id':123,'statuscode':'', 'sn_list':"yyy"}
a = EncDec()
b = a.enc_data(str(x))
print("ENC DATA",b)
print("ENC DATA",type(b))
print("ENC DATA",b[0])
print("ENC DATA",b[1])
#c = a.dec_data(b)
#print("DEC DATA",c)
