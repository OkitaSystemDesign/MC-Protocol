# MC Protocol Frame3E (UDP/IP)

from socket import *
import struct
import logging

BUFSIZE = 4096
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

class MCProtcol3E:
    addr = ()

    def __init__(self, host, port, timeout=2.0):
        self.addr = host, port
        self.s = socket(AF_INET, SOCK_DGRAM)
        self.s.settimeout(timeout)

    def __del__(self):
        self.s.close()

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

    def mcprotocol(self, cmd):
        senddata = self.mcpheader(cmd) + cmd

        # 送信ログ
        logger.debug(f"Send: {senddata.hex()}")

        self.s.sendto(senddata, self.addr)
        res = self.s.recv(BUFSIZE)

        # 受信ログ
        logger.debug(f"Recv: {res.hex()}")

        #self.s.close()

        if res[9] == 0 and res[10] == 0:
            data = res[11:]
            return data
        else:
            return None

    def read(self, memaddr, readsize, unitOfBit = False):
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

        data = self.mcprotocol(cmd)

        return data

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

        data = self.mcprotocol(cmd)

        return data


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

        # MC Protocol
        cmd = bytearray(4 + 2 + len(wdary) + len(dwdary))

        cmd[0] = 0x03                     # Random Read
        cmd[1] = 0x04
        cmd[2] = 0x00
        cmd[3] = 0x00

        cmd[4] = len(wd)
        cmd[5] = len(dwd)

        cmd[6:] = wdary + dwdary

        data = self.mcprotocol(cmd)

        return data

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

        # MC Protocol
        cmd = bytearray(4 + 2 + len(wdary) + len(dwdary))

        cmd[0] = 0x01                     # SetMonitor Command
        cmd[1] = 0x08
        cmd[2] = 0x00
        cmd[3] = 0x00

        cmd[4] = len(wd)
        cmd[5] = len(dwd)

        cmd[6:] = wdary + dwdary

        data = self.mcprotocol(cmd)

        return data

    # Get Monitor
    def MonitorGet(self):
        # MC Protocol
        cmd = bytearray(4)
        cmd[0] = 0x02                     # Write Command
        cmd[1] = 0x08
        cmd[2] = 0x00
        cmd[3] = 0x00

        data = self.mcprotocol(cmd)

        return data


    def toBin(self, data):
        size = len(data) * 2
        strBin = bin(int(data.hex(), 2))[2:]
        outdata = (('0' * size) + strBin)[-size:]

        return outdata

    def WordToBin(self, data):
        size = len(data) * 8
        strBin = format(int.from_bytes(data, 'little'), 'b')
        outdata = (('0' * (size)) + strBin) [-size:]

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
        s = [0]*(len(data) + 1)
        for i in range(0, len(data), 2):
            s[i] = data[i+1]
            s[i+1] = data[i]
        
        idx = s.index(0)
        b = bytes(s[:idx]).decode("utf-8")

        return b
