import time

class PackageMounter():
	"""
	"""
	def __init__(self, head, payLoad, EOP):
		self.head      = head
		self.payLoad   = payLoad
		self.EOP       = EOP
		self.maxSize   = 128
		self.leftovers = None
		#==============================================================
		# stuff the payload
		payload = payload.replace(EOP, eop_stuffed)
		#==============================================================
		# make the size of the payload 128
		totalSize = 16+len(self.payLoad)
		if totalSize > self.maxSize:
			self.payLoad   = self.payLoad[:self.maxSize]
			self.leftovers = self.payLoad[self.maxSize:]
        #==============================================================
		# adding the payload size to the head
		payLoadSize = len(self.payLoad)
		self.head = self.head + payLoadSize.to_bytes(1, "big")
		#==============================================================
		# create the package with head payload and EOP
		self.package = self.head + self.payLoad + self.EOP

	def getPackage(self):
		return self.package
	
	def getLeftovers(self):
		return self.leftovers

class HeadDismounter():
	def __init__(self, head):
		self.head = head
		# print("head",head)
		# print(self.head[0], self.head[1], self.head[2], self.head[3])
		self.packageNumber   = self.head[0] + self.head[1] + self.head[2] + self.head[3]
		self.message         = self.head[4] 
		self.totalOfPackages = self.head[5] + self.head[6] + self.head[7] + self.head[8]
		self.extension       = self.head[9]
		self.payLoadSize     = self.head[11]

	def getExtension(self):
		return self.extension

	def getMessage(self):
		return self.message

	def getPackageNumber(self):
		return self.packageNumber
	
	def getTotalOfPackages(self):
		return self.getTotalOfPackages

	def getPayLoadSize(self):
		return self.payLoadSize
	

class PackageDismounter():
	"""
	"""
	def __init__(self, package, head, previous_package):
		self.package           = package
		self.package_size      = len(package)

		self.head            = head
		self.packageNumber   = self.head[0] + self.head[1] + self.head[2] + self.head[3]
		self.message         = self.head[4] 
		self.totalOfPackages = self.head[5] + self.head[6] + self.head[7] + self.head[8]
		self.extension       = self.head[9]
		self.payLoadSize     = self.head[11]

		eop = bytes([0xf1]) + bytes([0xf2]) + bytes([0xf3]) + bytes([0xf4])
		eop_stuffed =  bytes([0x00]) + bytes([0xf1]) + bytes([0x00]) + bytes([0xf2]) \
					 + bytes([0x00]) + bytes([0xf3]) + bytes([0x00]) + bytes([0xf4])

		self.payLoad_EOP     = self.package[:]

		self.payLoad = None
		# print("package", self.package)
		# print("payload+EOP",self.payLoad_EOP)

		#=======================================================
		self.EOP_position = self.payload_EOP.find(eop)
		
		payload_stuffed = self.payload_EOP[:self.EOP_position]
		self.payload = payload_stuffed.replace(eop_stuffed, eop)

		if self.EOP_position == -1 or self.EOP_position != self.payload_size:
			self.message_sent = bytes([0x06])
		else:
			self.message_sent = bytes([0x04])

	def get_message_sent(self):
		return self.message_sent
	
	def getOverHead(self):
		return self.packageSize/self.payLoadSize
	
	def get_EOP_position(self):
		return self.EOP_position
	
	def getPayLoad(self):
		return self.payLoad

	def getPackageNumber(self):
		return self.packageNumber
	
	def getTotalOfPackages(self):
		return self.totalOfPackages
		

'''
response:
	- 0x01: EOP not found
	- 0x02: EOP wrong position
	- 0x03: payLoadSize != realPlayLoadSize
	- 0x04: wrong packageNumber
	- 0x05: success 
	- 0x06: timeout
	- 0xff: none

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
headSize = 12
#                   packageNumber   packageNumber   packageNumber    packageNumber    response        totalPackages   totalPackages   totalPackages   totalPackages   extension       ??
# head     	      = bytes([0x00])   + bytes([0x00]) + bytes([0x00]) + bytes([0x01]) + bytes([0xff]) + bytes([0x00]) + bytes([0x00]) + bytes([0x00]) + bytes([0x01]) + bytes([0xff]) + bytes([0x00])
# payLoad  	      = bytes([0xff])*5 + bytes([0xf1]) + bytes([0xf2]) + bytes([0xf3]) + bytes([0xf4]) + bytes([0xff])*200    
# EOP      	      = bytes([0xf1])   + bytes([0xf2]) + bytes([0xf3]) + bytes([0xf4])
# packageMounter    = PackageMounter(head=head, payLoad=payLoad, EOP=EOP)
# package           = packageMounter.getPackage()

# packageDismounter = PackageDismounter(package=package)
# response 		  = packageDismounter.getResponse()
# print(response)