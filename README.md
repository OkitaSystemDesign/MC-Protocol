# MC-Protocol
三菱 シーケンサの通信プロトコル MCプロトコル を使ってPythonからデバイスの値を読み書きする

# mcp.py
OMRON FINS protocol UDP connection  
Memory Area Read Write

# Constructor
fins(host, destFinsAddress, sorceFinsAddres)

# Functions
### fins.read(memAddres, size)
Memory Area Read  
memAddress = D0-D32767, E0_0-EF_32767, W0-511, 0-6143  
Return: bytes()

### fins.write(memAddres, data)
Memory Area Write  
memAddress = D0-D32767, E0_0-EF_32767, W0-511, 0-6143  
data = bytes()  
Return: fins responce

### fins.toInt16(data)
Convert to 16bit data  
### fins.toInt32(data)
Convert to 32bit data  
### fins.toInt64(data)
Convert to 64bit data  
### fins.toUInt16(data)
Convert to Unsigned 16bit data  
### fins.toUInt32(data)
Convert to Unsigned 32bit data  
### fins.toUInt64(data)
Convert to Unsigned 64bit data  
### fins.toFloat(data)
Convert to Float data  
### fins.toDouble(data)
Convert to Double data  

 return: list
 

# Example
```
finsudp = fins('192.168.250.1', '0.1.0', '0.10.0')
data = finsudp.read('E0_30000", 10)
print(finsudp.toInt16(data))
rcv = finsudp.write('E0_0', data)
print(rcv)
```

# Qiita記事
https://qiita.com/OkitaSystemDesign/items/7a958388d16c162148b2
