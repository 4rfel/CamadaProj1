
import subprocess

def install(name):
	subprocess.call(['pip', 'install', name])
try:
    from crccheck.crc import Crc64
except:
    install("crccheck")
finally:
    from crccheck.crc import Crc64



data = bytes([0xff])*64

crcData1 = Crc64.calc(data)
crcData2 = Crc64.calc(data)
crcData3 = Crc64.calc(data)
crcData4 = Crc64.calc(data)

# checksum = Checksum32.calc(data)
crcData = crcData1# + crcData2 + crcData3 + crcData4
# print(crcData, checksum)
print(crcData.to_bytes(8, "big"))
