import struct
import sys
import binascii
from Crypto.Cipher import AES
Signature = '\x89PNG\r\n\x1a\n'

f_source = 'pv02.PNG'
f_cible = 'Iota_logo.PNG'
f_resultat = 'test.PNG'

algo = AES
TB= 16

padding = lambda s: s + (TB - len(s) % TB) * chr(TB - len(s) % TB)

key = "MySecretKey12346"

with open(f_source, "rb") as f:
    s = padding(f.read())

with open(f_cible, "rb") as f:
    c = padding(f.read())

p = s[:TB] #premmier bloc
ecb_dec = algo.new(key, algo.MODE_ECB)

assert TB >= 16
size = len(s) - TB

chunktype = 'aaaa'

cy = Signature + struct.pack(">I",size) + chunktype

cy = ecb_dec.decrypt(cy)
IV = "".join([chr(ord(cy[i]) ^ ord(p[i])) for i in range(TB)])

cbc_enc = algo.new(key, algo.MODE_CBC, IV)
resultat = cbc_enc.encrypt(s)

resultat = resultat + struct.pack(">I", binascii.crc32(resultat[12:]) % 0x100000000)
resultat = resultat + c[8:]

with open(f_resultat, "wb") as f:
    f.write(resultat)

print """from Crypto.Cipher import %(algo)s
algo = %(algo)s.new(%(key)s, %(algo)s.MODE_CBC, %(IV)s)
with open(%(source)s, "rb") as f:
	d = f.read()
d = algo.encrypt(d)
with open("dec-" + %(target)s, "wb") as f:
	f.write(d)""" % {
        'algo': algo.__name__.split(".")[-1],
        'key':`key`,
        'IV':`IV`,
        'source':`f_resultat`,
'target':`f_source + "i"`}

