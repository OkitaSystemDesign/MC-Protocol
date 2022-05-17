# MC-Protocol
三菱 シーケンサの通信プロトコル MCプロトコル を使ってPythonからデバイスの値を読み書きする

# mcp.py
Mitsubishi MC Protocol Frame3E UDP/IP connection  
Device Read Write

# Constructor
MCProtcol3E(host, port)

# Functions
### read(memAddres, size, unitOfBit)
Device Area Read  
memAddress = X, Y, M, L, F, V, B, D, W, TS, TC, TN, SS, SC, SN, CS, CC, CN, SB, SW, S ,DX, DY, SM, SD  
size = 読出し点数  
unionOfBit = True ＝ ビット単位 / False = ワード単位  
Return: bytes()  

### write(memAddres, data, bitSize)
Memory Area Write  
memAddress = X, Y, M, L, F, V, B, D, W, TS, TC, TN, SS, SC, SN, CS, CC, CN, SB, SW, S ,DX, DY, SM, SD  
data = bytes()  
bitSize = ビット数（ビット単位で書込みするときのみ指定）  
Return: responce

### RandomRead(worddevice, dworddevice)
Memory Area Random Read ワード単位、ダブルワード単位の不連続デバイスの読出し  
memAddress = X, Y, M, L, F, V, B, D, W, TN, SN, CN, SB, SW, S ,DX, DY, SM, SD  
worddevice = ワード読出しアドレス（カンマ区切り）  
dworddvice = ダブルワード読出しアドレス（カンマ区切り）  
Return: bytes()

### MonitorSet(worddevice, dworddevice)
Monitor registration モニタするデバイスを登録  
memAddress = X, Y, M, L, F, V, B, D, W, TN, SN, CN, SB, SW, S ,DX, DY, SM, SD  
worddevice = ワード読出しアドレス（カンマ区切り）  
dworddvice = ダブルワード読出しアドレス（カンマ区切り）  
Return: responce

### MonitorGet()
Monitor 登録したデバイスの値を読み出す  
memAddress = X, Y, M, L, F, V, B, D, W, TN, SN, CN, SB, SW, S ,DX, DY, SM, SD  
worddevice = ワード読出しアドレス（カンマ区切り）  
dworddvice = ダブルワード読出しアドレス（カンマ区切り）  
Return: bytes()


### toBin(data)
Convert to Bit data  
### WordToBin(data)
Convert word data to Bit data  
### toInt16(data)
Convert to 16bit data  
### toInt32(data)
Convert to 32bit data  
### toInt64(data)
Convert to 64bit data  
### toUInt16(data)
Convert to Unsigned 16bit data  
### toUInt32(data)
Convert to Unsigned 32bit data  
### toUInt64(data)
Convert to Unsigned 64bit data  
### toFloat(data)
Convert to Float data  
### toDouble(data)
Convert to Double data  
### toString(data)
Convert to String data  

 return: list
 

# Example
```
# example
# set IPAddress,Port
mcp = MCProtcol3E('192.168.0.41', 4999)

# words
data = mcp.read('D10000', 1)
print(mcp.toInt16(data))        # convert int16    out> [0]
rcv = mcp.write('D10', data)
print(rcv)                      # normal recieve  out> b'\x00\x00'

# bits
#data = mcp.read('M8000', 8, True)
data = mcp.read('M0', 16, True)
print(data)                     # out> b'\x00\x00\x00\x00\x00\x00\x00\x00
print(mcp.toBin(data))          # out> 0000000000000000
rcv = mcp.write('M100', data, 8)
print(rcv)                      # out> b'\x00\x00'

data = mcp.read('D0', 1, False)
print(mcp.WordToBin(data))      # out> 0000000000000000

# numeric
data = struct.pack('hhh', 123, 456, 789)
rcv = mcp.write('D20', data)
print(rcv)                      # out> b'\x00\x00'
# float
data = struct.pack('f', 1.23)
rcv = mcp.write('D10020', data)
print(rcv)                      # out> b'\x00\x00'
# bits
data = [0x11, 0x11, 0x10]
rcv = mcp.write('M8100', data, 5)

# RandomRead
rcv = mcp.RandomRead('D0,TN0,M100,X20', 'D1500,Y160,M1111')
print(rcv)                      # out> b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
print(mcp.toInt16(rcv[:8]))     # out> [0, 0, 0, 0]
print(mcp.toInt32(rcv[8:]))     # out> [0, 0, 0]

# Monitor
data = mcp.MonitorSet('D50, D55', 'D60, D64')
rcv = mcp.MonitorGet()
print(mcp.toInt16(rcv[:4]))    # out> [50, 55]
print(mcp.toInt32(rcv[4:]))    # out> [3997756, 4259904]
```

# Qiita記事
https://qiita.com/OkitaSystemDesign/items/97b7d27c0d53668baafc
