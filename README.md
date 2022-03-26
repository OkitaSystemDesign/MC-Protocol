# MC-Protocol
三菱 シーケンサの通信プロトコル MCプロトコル を使ってPythonからデバイスの値を読み書きする

# mcp.py
Mitsubishi MC Protocol Frame3E UDP/IP connection  
Device Read Write

# Constructor
MCProtcol3E(host, port)

# Functions
### .read(memAddres, size, unitOfBit)
Device Area Read  
memAddress = X, Y, M, L, F, V, B, D, W, TS, TC, TN, SS, SC, SN, CS, CC, CN, SB, SW, S ,DX, DY, SM, SD  
size = 読出し点数
unionOfBit = True ＝ ビット単位 / False = ワード単位  
Return: bytes()

### .write(memAddres, data, bitSize)
Memory Area Write  
memAddress = X, Y, M, L, F, V, B, D, W, TS, TC, TN, SS, SC, SN, CS, CC, CN, SB, SW, S ,DX, DY, SM, SD  
data = bytes()  
bitSize = ビット数（ビット単位で書込みするときのみ指定）  
Return: responce

### .toBit(data)
Convert to Bit data  
### .toInt16(data)
Convert to 16bit data  
### .toInt32(data)
Convert to 32bit data  
### .toInt64(data)
Convert to 64bit data  
### .toUInt16(data)
Convert to Unsigned 16bit data  
### .toUInt32(data)
Convert to Unsigned 32bit data  
### .toUInt64(data)
Convert to Unsigned 64bit data  
### .toFloat(data)
Convert to Float data  
### .toDouble(data)
Convert to Double data  
### .toString(data)
Convert to String data  

 return: list
 

# Example
```
mcp = MCProtcol3E('192.168.0.41', 4999)
# words
data = mcp.read('D0', 10)
print(mcp.toInt16(data))        # convert int16
rcv = mcp.write('D10', data)
print(rcv)                      # normal recieve = 0x00 0x00

# bits
data = mcp.read('SM0', 8, True)
print(mcp.toBin(data))          # convert bin
rcv = mcp.write('M0', data, True)
print(rcv)


# numeric
data = struct.pack('hhh', 123, 456, 789)
rcv = mcp.write('D20', data)
# float
data = struct.pack('f', 1.23)
rcv = mcp.write('D30', data)
# bits
data = [0x11, 0x11, 0x10]
rcv = mcp.write('M10', data, 5)
```

# Qiita記事
https://qiita.com/OkitaSystemDesign/items/7a958388d16c162148b2
