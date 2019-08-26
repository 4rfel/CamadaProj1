import time

class PackageMounter():
	"""
	"""
	def __init__(self, head, payLoad, EOP):
		self.head      = head
		self.EOP       = EOP
		self.maxSize   = 2**7
		self.leftovers = None
		eop_stuffed =  bytes([0x00]) + bytes([0xf1]) + bytes([0x00]) + bytes([0xf2]) + bytes([0x00]) + bytes([0xf3]) + bytes([0x00]) + bytes([0xf4])
		#==============================================================
		# stuff the payload
		self.payLoad = payLoad.replace(EOP, eop_stuffed) 
		#==============================================================
		# make the size of the payload 2**7
		totalSize = 16+len(self.payLoad)
		if totalSize > self.maxSize:
			self.payLoad   = self.payLoad[:self.maxSize]
			self.leftovers = self.payLoad[self.maxSize:]
        #==============================================================
		# adding the payload size to the head
		payLoadSize = len(self.payLoad)
		self.head = self.head + bytes([payLoadSize])
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
		self.packageNumber   = int.from_bytes(self.head[0:4], "big")
		self.message         = self.head[4 ] 
		self.totalOfPackages = int.from_bytes(self.head[5:9], "big")
		self.extension       = self.head[9 ]
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
	def __init__(self, package, head):
		self.package         = package
		self.packageSize     = len(package)

		self.head            = head
		self.packageNumber   = int.from_bytes(self.head[1:4], "big")
		self.message         = self.head[4] 
		self.totalOfPackages = int.from_bytes(self.head[5:9], "big")
		self.extension       = self.head[9]
		self.payLoadSize     = self.head[11]

		self.payLoad_EOP     = self.package[:]

		eop = bytes([0xf1]) + bytes([0xf2]) + bytes([0xf3]) + bytes([0xf4])
		eop_stuffed =  bytes([0x00]) + bytes([0xf1]) + bytes([0x00]) + bytes([0xf2]) + bytes([0x00]) + bytes([0xf3]) + bytes([0x00]) + bytes([0xf4])

		self.payLoad = None
		#=======================================================
		self.timeOut  = False
		startTime     = time.time()
		#=======================================================
		self.EOPPosition = self.payLoad_EOP.find(eop)
		
		payLoad_stuffed = self.payLoad_EOP[:self.EOPPosition]
		self.payLoad = payLoad_stuffed.replace(eop_stuffed, eop)
		if self.EOPPosition == -1:
			self.MSG0x01()
		else:
			self.MSG0x05()
		#==============================================================
		# mount the response package
		payLoadResponse = bytes([0x00])
		EOP 			= bytes([0xf1]) + bytes([0xf2]) + bytes([0xf3])+ bytes([0xf4])
		packageMounter  = PackageMounter(head=self.headResponse, payLoad=payLoadResponse, EOP=EOP) 
		#==============================================================
		# send the response
		self.response = packageMounter.getPackage()
		#==============================================================


#                                 packageNumber                    response        totalPackages                              extension      
	def MSG0x01(self):
		self.headResponse = self.packageNumber.to_bytes(4, "big") + bytes([0x01]) + self.totalOfPackages.to_bytes(4, "big") + bytes([0xff]) + bytes([0x00])
		print(self.payLoad_EOP)
		print("0x01 - EOP not found")

	def MSG0x02(self):
		self.headResponse = self.packageNumber.to_bytes(4, "big") + bytes([0x02]) + self.totalOfPackages.to_bytes(4, "big") + bytes([0xff]) + bytes([0x00])
		print("0x02 - EOP wrong position")
	
	def MSG0x03(self):
		self.headResponse = self.packageNumber.to_bytes(4, "big") + bytes([0x03]) + self.totalOfPackages.to_bytes(4, "big") + bytes([0xff]) + bytes([0x00])
		print("0x03 - payLoadSize != realPlayLoadSize")
	
	def MSG0x04(self):
		self.headResponse = self.packageNumber.to_bytes(4, "big") + bytes([0x04]) + self.totalOfPackages.to_bytes(4, "big") + bytes([0xff]) + bytes([0x00])
		print("0x04 - wrong packageNumber")
	
	def MSG0x05(self):
		self.foundEOP = True
		self.headResponse = self.packageNumber.to_bytes(4, "big") + bytes([0x05]) + self.totalOfPackages.to_bytes(4, "big") + bytes([0xff]) + bytes([0x00])
		print("0x05 - success")

	def MSG0x06(self):
		self.headResponse = self.packageNumber.to_bytes(4, "big") + bytes([0x06]) + self.totalOfPackages.to_bytes(4, "big") + bytes([0xff]) + bytes([0x00])
		print("0x06 - timeout")
		
	def getResponse(self):
		return self.response
	
	def setTimeOutFalse(self):
		self.timeOut = False
	
	def getExtencin(self):
		return self.extension
	
	def getMessage(self):
		return self.message
	
	def getOverHead(self):
		return self.packageSize/self.payLoadSize
	
	def getEOPPosition(self):
		return self.EOPPosition
	
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

# packageDismounter = PackageDismounter(package=package,head)
# response 		  = packageDismounter.getResponse()
# print(response)
