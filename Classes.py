class HeadDismounter():
	def _init_(self, head):
		self.head = head
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
	
	def getHead(self):
		return self.head

	def getPayloadSize(self):
		return self.payLoadSize