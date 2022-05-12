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
            moffset = list((address).to_bytes(3,'little'))

        elif mtype == 'TS' or mtype == 'TC' or mtype == 'TN' or mtype == 'SS'\
                or mtype == 'SC' or mtype == 'SN' or mtype == 'CS' or mtype == 'CC'\
                or mtype == 'CN' or mtype == 'SM' or mtype == 'SD':
            address = int(adr[2:])
            moffset = list((address).to_bytes(3,'little'))

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
            moffset = list((address).to_bytes(3,'little'))

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


    def mcpheader(self, cmd):
        ary = bytearray(11)
        requestdatalength = struct.pack("<H", len(cmd) + 2)

        ary[0] = 0x50                      # sub header
        ary[1] = 0x00
        ary[2] = 0x00                      # Network No.
        ary[3] = 0xFF                      # PC No.
        ary[4] = 0xFF                      # Request destination module i/o No.
        ary[5] = 0x03
        ary[6] = 0x00                      # Request destination module station No.
        ary[7] = requestdatalength[0]      # Request data length
        ary[8] = requestdatalength[1]
        ary[9] = 0x10                      # CPU monitoring timer
        ary[10] = 0x00

        return ary


    def read(self, memaddr, readsize, unitOfBit = False):
        s = socket(AF_INET, SOCK_DGRAM)
        s.settimeout(2)

        # MC Protocol
        cmd = bytearray(10)
        cmd[0] = 0x01                     # Read Command
        cmd[1] = 0x04
        if unitOfBit:
            cmd[2] = 0x01                 # Sub Command
            cmd[3] = 0x00
        else:
            cmd[2] = 0x00
            cmd[3] = 0x00

        deviceCode, memoffset = self.offset(memaddr)
        cmd[4] = memoffset[0]             # head device
        cmd[5] = memoffset[1]                     
        cmd[6] = memoffset[2]
        cmd[7] = deviceCode               # Device code

        rsize = struct.pack("<H", readsize)
        cmd[8] = rsize[0]                 # Number of device
        cmd[9] = rsize[1]

        senddata = self.mcpheader(cmd) + cmd
        s.sendto(senddata, self.addr)

        res = s.recv(BUFSIZE)
        if res[9] == 0 and res[10] == 0:
            data = res[11:]
            return data
        else:
            return None


    def write(self, memaddr, writedata, bitSize = 0):
        if bitSize > 0:
            unitOfBit = True
            if bitSize <= (len(writedata) * 2):
                elementCnt = bitSize
                writedata = writedata[:(bitSize + 1) // 2]
            else:
                return
        else:
            unitOfBit = False
            if len(writedata) % 2 == 0:
                elementCnt = len(writedata) // 2
            else:
                return

        s = socket(AF_INET, SOCK_DGRAM)
        s.settimeout(2)

        # MC Protocol
        elementSize = struct.pack("<H", elementCnt)

        cmd = bytearray(10 + len(writedata))
        cmd[0] = 0x01                     # Write Command
        cmd[1] = 0x14
        if unitOfBit:
            cmd[2] = 0x01                 # Sub Command
            cmd[3] = 0x00
        else:
            cmd[2] = 0x00
            cmd[3] = 0x00

        deviceCode, memoffset = self.offset(memaddr)
        cmd[4] = memoffset[0]             # head Dvice
        cmd[5] = memoffset[1]                     
        cmd[6] = memoffset[2]
        cmd[7] = deviceCode               # Device code
        cmd[8] = elementSize[0]           # Element Size
        cmd[9] = elementSize[1]
        cmd[10:] = writedata

        senddata = self.mcpheader(cmd) + cmd
        s.sendto(senddata, self.addr)
        rcv = s.recv(BUFSIZE)

        return rcv[9:]


    # Random Read
    def RandomRead(self, worddevice, dworddevice):

        wd = worddevice.replace(' ', '').split(',')
        wdary = []
        if len(wd) > 0:
            for d in wd:
                code, offset = self.offset(d)
                wdary.extend(offset)
                wdary.append(code)

        dwd = dworddevice.replace(' ', '').split(',')
        dwdary = []
        if len(dwd) > 0:
            for dw in dwd:
                code, offset = self.offset(dw)
                dwdary.extend(offset)
                dwdary.append(code)


        s = socket(AF_INET, SOCK_DGRAM)
        s.settimeout(2)

        # MC Protocol
        cmd = bytearray(4 + 2 + len(wdary) + len(dwdary))

        cmd[0] = 0x03                     # Random Read
        cmd[1] = 0x04
        cmd[2] = 0x00
        cmd[3] = 0x00

        cmd[4] = len(wd)
        cmd[5] = len(dwd)

        cmd[6:] = wdary + dwdary

        senddata = self.mcpheader(cmd) + cmd
        s.sendto(senddata, self.addr)
        res = s.recv(BUFSIZE)

        if res[9] == 0 and res[10] == 0:
            data = res[11:]
            return data
        else:
            return None

    # Set Monitor
    def MonitorSet(self, worddevice, dworddevice):

        wd = worddevice.replace(' ', '').split(',')
        wdary = []
        if len(wd) > 0:
            for d in wd:
                code, offset = self.offset(d)
                wdary.extend(offset)
                wdary.append(code)

        dwd = dworddevice.replace(' ', '').split(',')
        dwdary = []
        if len(dwd) > 0:
            for dw in dwd:
                code, offset = self.offset(dw)
                dwdary.extend(offset)
                dwdary.append(code)


        s = socket(AF_INET, SOCK_DGRAM)
        s.settimeout(2)

        # MC Protocol
        cmd = bytearray(4 + 2 + len(wdary) + len(dwdary))

        cmd[0] = 0x01                     # SetMonitor Command
        cmd[1] = 0x08
        cmd[2] = 0x00
        cmd[3] = 0x00

        cmd[4] = len(wd)
        cmd[5] = len(dwd)

        cmd[6:] = wdary + dwdary

        senddata = self.mcpheader(cmd) + cmd
        s.sendto(senddata, self.addr)
        rcv = s.recv(BUFSIZE)

        return rcv[9:]

    # Get Monitor
    def MonitorGet(self):
        s = socket(AF_INET, SOCK_DGRAM)
        s.settimeout(2)

        # MC Protocol
        cmd = bytearray(4)
        cmd[0] = 0x02                     # Write Command
        cmd[1] = 0x08
        cmd[2] = 0x00
        cmd[3] = 0x00

        senddata = self.mcpheader(cmd) + cmd
        s.sendto(senddata, self.addr)
        rcv = s.recv(BUFSIZE)
        return rcv[11:]


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
        
        idx = s.index(0)
        b = bytes(s[:idx]).decode("utf-8")

        return b

if __name__ == "__main__":

    # example
    # set IPAddress,Port
    mcp = MCProtcol3E('192.168.0.41', 4999)

    # words
    data = mcp.read('D10000', 1)
    print(mcp.toInt16(data))        # convert int16
    rcv = mcp.write('D10', data)
    print(rcv)                      # normal recieve = 0x00 0x00

    # bits
    data = mcp.read('M8000', 8, True)
    print(data)
    print(mcp.toBin(data))          # convert bin
    rcv = mcp.write('M100', data, 8)
    print(rcv)

    # numeric
    data = struct.pack('hhh', 123, 456, 789)
    rcv = mcp.write('D20', data)
    print(rcv)
    # float
    data = struct.pack('f', 1.23)
    rcv = mcp.write('D10020', data)
    print(rcv)
    # bits
    data = [0x11, 0x11, 0x10]
    rcv = mcp.write('M8100', data, 5)

    # RandomRead
    rcv = mcp.RandomRead('D0,TN0,M100,X20', 'D1500,Y160,M1111')
    print(rcv)
    print(mcp.toInt16(rcv[:8]))
    print(mcp.toInt32(rcv[8:]))
    
    # Monitor
    data = mcp.MonitorSet('D50, D55', 'D60, D64')
    rcv = mcp.MonitorGet()
    print(mcp.toInt16(rcv[:4]))
    print(mcp.toInt32(rcv[4:]))

