from Crypto.Cipher import AES

aes = AES.new("MySecretKey12346", AES.MODE_CBC, 'V[\xaeu\x18v%\xbfg=C7\xfe\r\x8d\xf6')
TB = 16
padding = lambda d: d + (TB - len(d) % TB) * chr(TB - len(d) % TB)

with open("test.PNG", "rb") as f:
	d = padding(f.read())




d = aes.decrypt(d)

with open("file.PNG", "wb") as f:
        f.write(d)
