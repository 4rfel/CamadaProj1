import time
import subprocess
def install(name):
	subprocess.call(['pip', 'install', name])

try:
    from crccheck.crc import Crc16
except:
    install("crccheck")
finally:
    from crccheck.crc import Crc16


class PackageMounter():
	"""
	"""
	def __init__(self, head, payload):
		EOP         = bytes([0xf1]) + bytes([0xf2]) + bytes([0xf3]) + bytes([0xf4])
		eop_stuffed = bytes([0x00]) + bytes([0xf1]) + bytes([0x00]) + bytes([0xf2])\
					+ bytes([0x00]) + bytes([0xf3]) + bytes([0x00]) + bytes([0xf4])
		#==============================================================
		# stuff the payload
		payload = payload.replace(EOP, eop_stuffed)
		#==============================================================
		# make the size of the payload 2**7
		totalSize = len(payload)
		self.leftovers = bytearray()
		if totalSize > 128:
			payload   = payload[:128]
			self.leftovers = payload[128:]
        #==============================================================
		# adding the payload size to the head
		payload_size = len(payload)
		# print(f"payload size: {payload_size}")
		head = head + bytes([payload_size])
		#==============================================================
		crcData0 = Crc16.calc(payload)

		crcData0_bytes = int(crcData0).to_bytes(2, "big")

		head = head + crcData0_bytes

		# create the package with head payload and EOP
		self.package = head + payload + EOP

	def get_package(self):
		return self.package
	
	def get_leftovers(self):
		return self.leftovers


class Head():
# packageNumber*3 + response*1 + totalPackages*3 + extension*1 + servidor number*1 + payload size*1 + crc64*8 + crc64*8 = 26bytes
	def __init__(self, head):
		self.head              = head

		self.current_package   = int.from_bytes(self.head[0:3], "big")
		self.message           = self.head[3] 
		self.total_of_packages = int.from_bytes(self.head[4:7], "big")
		self.extension         = self.head[7]
		self.server_number     = self.head[8]
		self.payload_size      = self.head[9]
		self.crc64             = self.head[10:]

	def get_crc(self):
		return self.crc64

	def get_extension(self):
		return self.extension

	def get_message(self):
		return self.message

	def get_current_package(self):
		return self.current_package
	
	def get_total_of_packages(self):
		return self.total_of_packages

	def get_payload_size(self):
		return self.payload_size

	def get_server_number(self):
		return self.server_number
	

class PackageDismounter():
	"""
	"""
	def __init__(self, package, head):
		self.package           = package
		self.package_size      = len(package)

		self.payload_size      = head.get_payload_size()

		eop = bytes([0xf1]) + bytes([0xf2]) + bytes([0xf3]) + bytes([0xf4])
		eop_stuffed =  bytes([0x00]) + bytes([0xf1]) + bytes([0x00]) + bytes([0xf2]) \
					 + bytes([0x00]) + bytes([0xf3]) + bytes([0x00]) + bytes([0xf4])

		payload_EOP = self.package[:]

		#=======================================================
		self.EOP_position = payload_EOP.find(eop)
		
		payload_stuffed = payload_EOP[:self.EOP_position]

		crcData0 = Crc16.calc(payload_stuffed)

		crcBytes = crcData0.to_bytes(2, "big")
		print(f"crc calc    : {crcBytes}")
		print(f"crc received: {head.get_crc()}")


		self.payload = payload_stuffed.replace(eop_stuffed, eop)

		if self.EOP_position != self.payload_size or crcBytes != head.get_crc():
			self.message_sent = bytes([0x06])
		else:
			self.message_sent = bytes([0x04])

	def get_message_sent(self):
		return self.message_sent
	
	def get_overhead(self):
		return self.package_size/self.payload_size
	
	def get_EOP_position(self):
		return self.EOP_position
	
	def get_payload(self):
		return self.payload

'''
response:
	- 0x01: connection request
	- 0x02: connection granted 
	- 0x03: sending data
	- 0x04: success
	- 0x05: timeout
	- 0x06: error

extension:
	- 0x00: .txt
	- 0x01: .py
	- 0x02: .png
	- 0x03: .jpg
	- 0x04: .jpeg
	- 0x05: .pdf
	- 0x06: .gif
	- 0x07: .docx
	- 0x08: .js
	- 0x09: .java
	- 0x0a: .dll
	- 0xff: sem extensão
'''
# packageNumber*3 + response*1 + totalPackages*3 + extension*1 + servidor number*1 + payload size*1 = 10bytes