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
		index = 3
		while index < len(self.payLoad)-3:
			f1 = self.payLoad[index-3]
			f2 = self.payLoad[index-2]
			f3 = self.payLoad[index-1]
			f4 = self.payLoad[index  ]
			index += 1

			if f1==0xf1 and f2==0xf2 and f3==0xf3 and f4==0xf4:
				self.payLoad = self.payLoad[:index-4] + bytes([0x00]) + self.payLoad[index-4:]
				self.payLoad = self.payLoad[:index-2] + bytes([0x00]) + self.payLoad[index-2:]
				self.payLoad = self.payLoad[:index  ] + bytes([0x00]) + self.payLoad[index:  ]
				self.payLoad = self.payLoad[:index+2] + bytes([0x00]) + self.payLoad[index+2:]
		#==============================================================
		# make the size of the payload 128
		totalSize = 16+len(self.payLoad)
		if totalSize > self.maxSize:
			self.payLoad = self.payLoad[:self.maxSize]
			self.leftovers = self.payLoad[self.maxSize:]

		# adding the payload size to the head
		payLoadSize = len(self.payLoad)
		self.head = self.head + payLoadSize.to_bytes(1, "big")

		# create the package with head payload and EOP
		self.package = self.head + self.payLoad + self.EOP

	def getPackage(self):
		return self.package
	
	def getLeftovers(self):
		return self.leftovers

	

class PackageDismounter():
	"""
	"""
	def __init__(self, package):
		self.package         = package
		self.packageSize     = len(package)
		self.EOPPosition     = None

		self.head            = package[:headSize]
		self.packageNumber   = self.head[0] + self.head[1] + self.head[2] + self.head[3]
		self.message         = self.head[4] 
		self.totalOfPackages = self.head[5] + self.head[6] + self.head[7] + self.head[8]
		self.extension       = self.head[9]
		self.payLoadSize     = self.head[11]
		self.payLoad_EOP     = self.package[headSize:]

		#=======================================================
		index         = 7
		self.foundEOP = False
		self.timeOut  = False
		startTime     = time.time()
		while index < len(self.payLoad_EOP):
		# test if we have a timeout
			deltaTime = time.time() - startTime
			if deltaTime >= 5:
				self.foundEOP = True
				self.MSG0x06()
				self.timeOut  = True
				break
		#=======================================================
		# searching for the EOP
			f1 = self.payLoad_EOP[index-3]
			f2 = self.payLoad_EOP[index-2]
			f3 = self.payLoad_EOP[index-1]
			f4 = self.payLoad_EOP[index  ]

			if f1==0xf1 and f2==0xf2 and f3==0xf3 and f4==0xf4:
				if index+1 != self.payLoadSize:
					print(index+1, self.payLoadSize)
					#response 0x02, EOP wrong position
					self.MSG0x02()
					self.foundEOP = True
				else:
					self.EOPPosition = index-3
					#response 0x05, success
					self.MSG0x05()
		#=============================================================
		# de-stuffing the payload
			x04 = self.payLoad_EOP[index-7]
			f1  = self.payLoad_EOP[index-6]
			x01 = self.payLoad_EOP[index-5]
			f2  = self.payLoad_EOP[index-4]
			x02 = self.payLoad_EOP[index-3]
			f3  = self.payLoad_EOP[index-2]
			x03 = self.payLoad_EOP[index-1]
			f4  = self.payLoad_EOP[index  ]
			index += 1

			if x01==0x00 and f1==0xf1 and x02==0x00 and f2==0xf2 and x03==0x00 and f3==0xf3 and x04==0x00 and f4==0xf4:
				self.payLoad_EOP = self.payLoad_EOP[:index-8] + self.payLoad_EOP[index-7:]
				self.payLoad_EOP = self.payLoad_EOP[:index-7] + self.payLoad_EOP[index-6:]
				self.payLoad_EOP = self.payLoad_EOP[:index-6] + self.payLoad_EOP[index-5:]
				self.payLoad_EOP = self.payLoad_EOP[:index-5] + self.payLoad_EOP[index-4:]
		#===============================================================
		# response 0x01, EOP not found
		if not self.foundEOP:
			self.MSG0x01()
		#==============================================================
		# mount the response package
		payLoadResponse = bytes([0x00])
		EOP = bytes([0xf1]) + bytes([0xf2]) + bytes([0xf3])+ bytes([0xf4])
		packageMounter = PackageMounter(head=self.headResponse, payLoad=payLoadResponse, EOP=EOP) 
		#==============================================================
		# send the package
		if not self.timeOut:
			self.response = packageMounter.getPackage()
		else:
			while self.timeOut:
				self.response = packageMounter.getPackage()
				time.sleep(0.1)
		#==============================================================


#                                 packageNumber                    response       totalPackages                           extension         ??

	def MSG0x01(self):
		self.headResponse = self.packageNumber.to_bytes(4, "big") + bytes([0x01]) + self.totalOfPackages.to_bytes(4, "big") + bytes([0xff]) + bytes([0x00])
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
	
	def getPackageNumber(self):
		return self.packageNumber
	
	def getTotalOfPackages(self):
		return self.getTotalOfPackages
		

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
#      packageNumber   packageNumber   packageNumber   packageNumber   response        totalPackages   totalPackages   totalPackages   totalPackages   extension       ??
head = bytes([0x00]) + bytes([0x00]) + bytes([0x00]) + bytes([0x01]) + bytes([0xff]) + bytes([0x00]) + bytes([0x00]) + bytes([0x00]) + bytes([0x01]) + bytes([0xff]) + bytes([0x00])
payLoad = bytes([0xff])*5 + bytes([0xf1]) + bytes([0xf2]) + bytes([0xf3])+ bytes([0xf4]) + bytes([0xff])*200    
EOP = bytes([0xf1]) + bytes([0xf2]) + bytes([0xf3])+ bytes([0xf4])
packageMounter = PackageMounter(head=head, payLoad=payLoad, EOP=EOP)
package = packageMounter.getPackage()

packageDismounter = PackageDismounter(package=package)
response = packageDismounter.getResponse()
print(response)
