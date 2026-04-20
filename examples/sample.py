from mcprotocol import MCProtcol3E
import struct

'''
# MCProtocolの送受信ログが必要な場合はコメントを外してください
import logging

logging.basicConfig(
    filename="mcp.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
'''

try:
    # example
    # set IPAddress,Port
    mcp = MCProtcol3E('192.168.250.41', 4999)

    # bits
    #data = mcp.read('M8000', 8, True)
    data = mcp.read('M0', 16, True)
    print(data)
    print(mcp.toBin(data))          # convert bin
    rcv = mcp.write('M100', data, 8)
    print(rcv)

    data = mcp.read('D0', 1, False)
    print(mcp.WordToBin(data))          # convert word to bin

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
    rcv = mcp.MonitorSet('D50, D55', 'D60, D64')
    print(rcv)
    rcv = mcp.MonitorGet()
    print(mcp.toInt16(rcv[:4]))
    print(mcp.toInt32(rcv[4:]))

except Exception as e:
    print(e)