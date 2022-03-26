# MC Protocol Frame3E (UDP/IP)

from socket import *
import struct

BUFSIZE = 4096

class MCProtcol3E:
    addr = ()

    def __init__(self, host, port):
        self.addr = host, port

    def offset(self, adr):
        moffset = [0] * 3

        mtype = adr[:2]
        if mtype == 'SB' or mtype == 'SW' or mtype == 'DX' or mtype == 'DY':
            address = int(adr[2:], 16)
            moffset = list((address).to_bytes(3,'big'))

        elif mtype == 'TS' or mtype == 'TC' or mtype == 'TN' or mtype == 'SS'\
                or mtype == 'SC' or mtype == 'SN' or mtype == 'CS' or mtype == 'CC'\
                or mtype == 'CN' or mtype == 'SM' or mtype == 'SD':
            address = int(adr[2:])
            moffset = list((address).to_bytes(3,'big'))

        if mtype == 'TS':
            deviceCode = 0xC1
        elif mtype == 'TC':
            deviceCode = 0xC0
        elif mtype == 'TN':
            deviceCode = 0xC2
        elif mtype == 'SS':
            deviceCode = 0xC7
        elif mtype == 'SC':
            deviceCode = 0xC6
        elif mtype == 'SN':
            deviceCode = 0xC8
        elif mtype == 'CS':
            deviceCode = 0xC4
        elif mtype == 'CC':
            deviceCode = 0xC3
        elif mtype == 'CN':
            deviceCode = 0xC5
        elif mtype == 'SB':
            deviceCode = 0xA1
        elif mtype == 'SW':
            deviceCode = 0xB5
        elif mtype == 'DX':
            deviceCode = 0xA2
        elif mtype == 'DY':
            deviceCode = 0xA3
        elif mtype == 'SM':
            deviceCode = 0x91
        elif mtype == 'SD':
            deviceCode = 0xA9
        else:
            mtype = adr[:1]
            if mtype == 'X' or mtype == 'Y' or mtype == 'B' or mtype == 'W':
                address = int(adr[1:], 16)
            else:
                address = int(adr[1:])
            moffset = list((address).to_bytes(3,'big'))

            if mtype == 'X':
                deviceCode = 0x9C
            elif mtype == 'Y':
                deviceCode = 0x9D
            elif mtype == 'M':
                deviceCode = 0x90
            elif mtype == 'L':
                deviceCode = 0x92
            elif mtype == 'F':
                deviceCode = 0x93
            elif mtype == 'V':
                deviceCode = 0x94
            elif mtype == 'B':
                deviceCode = 0xA0
            elif mtype == 'D':
                deviceCode = 0xA8
            elif mtype == 'W':
                deviceCode = 0xB4
            elif mtype == 'S':
                deviceCode = 0x98

        return deviceCode, moffset


    def read(self, memaddr, readsize, unitOfBit = False):
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind(('', self.addr[1]))
        s.settimeout(2)

        # MC Protocol
        senddata = bytearray(21)
        senddata[0] = 0x50                      # sub header
        senddata[1] = 0x00
        senddata[2] = 0x00                      # Network No.
        senddata[3] = 0xFF                      # PC No.
        senddata[4] = 0xFF                      # Request destination module i/o No.
        senddata[5] = 0x03
        senddata[6] = 0x00                      # Request destination module station No.
        senddata[7] = 0x0C                      # Request data length
        senddata[8] = 0x00
        senddata[9] = 0x10                      # CPU monitoring timer
        senddata[10] = 0x00
        senddata[11] = 0x01                     # Read Command
        senddata[12] = 0x04
        if unitOfBit:
            senddata[13] = 0x01                # Sub Command
            senddata[14] = 0x00
        else:
            senddata[13] = 0x00
            senddata[14] = 0x00

        deviceCode, memoffset = self.offset(memaddr)
        senddata[15] = memoffset[2]             # head device
        senddata[16] = memoffset[1]                     
        senddata[17] = memoffset[0]
        senddata[18] = deviceCode               # Device code

        rsize = struct.pack(">H", readsize)
        senddata[19] = rsize[1]                 # Number of device
        senddata[20] = rsize[0]

        s.sendto(senddata, self.addr)

        res = s.recv(BUFSIZE)
        data = res[11:]

        return data


    def write(self, memaddr, writedata, bitSize = 0):
        if bitSize > 0:
            unitOfBit = True
            if bitSize <= (len(writedata) * 2):
                elementCnt = bitSize
                writedata = writedata[:(bitSize + 1) // 2]
            else:
                return -1
        else:
            unitOfBit = False
            if len(writedata) % 2 == 0:
                elementCnt = len(writedata) // 2
            else:
                return -1

        s = socket(AF_INET, SOCK_DGRAM)
        s.bind(('', self.addr[1]))
        s.settimeout(2)

        # MC Protocol
        requestdatalength = struct.pack(">H", len(writedata) + 12)
        elementSize = struct.pack(">H", elementCnt)
        senddata = bytearray(21 + len(writedata))

        senddata[0] = 0x50                      # sub header
        senddata[1] = 0x00
        senddata[2] = 0x00                      # Network No.
        senddata[3] = 0xFF                      # PC No.
        senddata[4] = 0xFF                      # Request destination module i/o No.
        senddata[5] = 0x03
        senddata[6] = 0x00                      # Request destination module station No.
        senddata[7] = requestdatalength[1]      # Request data length
        senddata[8] = requestdatalength[0]
        senddata[9] = 0x10                      # CPU monitoring timer
        senddata[10] = 0x00
        senddata[11] = 0x01                     # Write Command
        senddata[12] = 0x14
        if unitOfBit:
            senddata[13] = 0x01                 # Sub Command
            senddata[14] = 0x00
        else:
            senddata[13] = 0x00
            senddata[14] = 0x00

        deviceCode, memoffset = self.offset(memaddr)
        senddata[15] = memoffset[2]             # head Dvice
        senddata[16] = memoffset[1]                     
        senddata[17] = memoffset[0]
        senddata[18] = deviceCode               # Device code
        senddata[19] = elementSize[1]           # Element Size
        senddata[20] = elementSize[0]
        senddata[21:] = writedata

        s.sendto(senddata, self.addr)
        rcv = s.recv(BUFSIZE)

        return rcv[9:]


    def toBin(self, data):
        outdata = bin(int(data.hex(), 2))

        return outdata

    def toInt16(self, data):
        outdata = []
        arydata = bytearray(data)
        for idx in range(0, len(arydata), 2):
            tmpdata = arydata[idx:idx+2]
            outdata += (struct.unpack('<h',tmpdata))
        
        return outdata

    def toUInt16(self, data):
        outdata = []
        arydata = bytearray(data)
        for idx in range(0, len(arydata), 2):
            tmpdata = arydata[idx:idx+2]
            outdata += (struct.unpack('<H',tmpdata))
        
        return outdata

    def toInt32(self, data):
        outdata = []
        arydata = bytearray(data)
        for idx in range(0, len(arydata), 4):
            tmpdata = arydata[idx:idx+4]
            outdata += (struct.unpack('<i',tmpdata))
        
        return outdata
            
    def toUInt32(self, data):
        outdata = []
        arydata = bytearray(data)
        for idx in range(0, len(arydata), 4):
            tmpdata = arydata[idx:idx+4]
            outdata += (struct.unpack('<I',tmpdata))
        
        return outdata

    def toInt64(self, data):
        outdata = []
        arydata = bytearray(data)
        for idx in range(0, len(arydata), 8):
            tmpdata = arydata[idx:idx+8]
            outdata += (struct.unpack('<q',tmpdata))
        
        return outdata

    def toUInt64(self, data):
        outdata = []
        arydata = bytearray(data)
        for idx in range(0, len(arydata), 8):
            tmpdata = arydata[idx:idx+8]
            outdata += (struct.unpack('<Q',tmpdata))
        
        return outdata

    def toFloat(self, data):
        outdata = []
        arydata = bytearray(data)
        for idx in range(0, len(arydata), 4):
            tmpdata = arydata[idx:idx+4]
            outdata += (struct.unpack('<f', tmpdata))
        return outdata

    def toDouble(self, data):
        outdata = []
        arydata = bytearray(data)
        for idx in range(0, len(arydata), 8):
            tmpdata = arydata[idx:idx+8]
            outdata += (struct.unpack('<d', tmpdata))
        return outdata

    def toString(self, data):
        s = [0]*len(data)
        for i in range(0, len(data), 2):
            s[i] = data[i+1]
            s[i+1] = data[i]
        
        b = bytes(s).decode("utf-8").replace("\00","")

        return b


# example
# set IPAddress,Port
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
