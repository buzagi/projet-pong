#/!/bin/python

import struct
import sys
import binascii

Signature = '\x89PNG\r\n\x1a\n'

#fichier_source, fichier_cible, fichier_dest, cle_chiffrement, algo = sys.argv[1:6]
fichier_source = 'date.txt'
fichier_cible = 'ressource.PNG'
fichier_dest = 'cyber.PNG'
cle_chiffrement = 'test12345'
algo = 'aes'
if algo.lower() == "3des":
    from Crypto.Cipher import DES3
    TB = 8
    algo = DES3
else:
    from Crypto.cipher import AES
    TB = 16
    algo = AES

padding = lambda s: s + (TB - len(s) % TB) * chr(BS - len(s) % TB) #padding


key = cle_chiffrement

with open(fichier_source, "rb") as f:
    s = padding(f.read())

with open(fichier_cible, "rb") as f:
    c = padding(f.read())

p = s[:TB] # premier bloc du plaintext

ecb_dec = algo.new(key, algo.MODE_ECB)

assert TB >= 2

taille = len(s) - TB

chuncktype = 'aaaa'

cypher = Signature + struct.pack(">I",size) + chunktype

cypher = ecb_dec.decrypt(cypher)
IV = "".join([chr(ord(cypher[i]) ^ ord(p[i])) for i in range(TB)])
cbc_enc = algo.new(key, algo.MODE_CBC, IV)
resultat = cbc_enc.encrypt(s)

# écriture du crc à la fin du chunck
resultat = resultat + struct.pack(">I", binascii.crc32(resultat[12:]) % 0x100000000)
# ajouter à la suite les données de c, en passant la signature
resultat = resultat + c[8:]

# on a le résultat, la clé et l'IV

cdc_dec = algo.new(key, algo.MODE_CBC, IV)
with open(fichier_dest, "wb") as f:
    f.write(cbc_dec.decrypt(padding(resultat)))


#génération du script






