from math import ceil
from classPackage import PackageDismounter, PackageMounter
from Classes import HeadDismounter
from enlace import enlace
from tkinter import Tk, filedialog
from time import time

class Master():
    '''
    Classe geral, que facilita a criação do server e Client, pois os dois compartilham de alguns padrões do protocolo, como os erros, tipos de extensão e a funação que monta o HEAD
    '''
    # def __init__(self,serialport):
    def __init__(self,serialport, comm):
        # self.comm = enlace(serialport)
        self.comm = comm
        self.head = None
        self.eop = bytes([0xF1]) + bytes([0xF2]) + bytes([0xF3]) + bytes([0xF4])
        self.payload = None
        self.extension_types = {'txt':0x00,'py':0x01,'png':0x02,'jpg':0x03,'jpeg':0x04,'pdf':0x05,'gif':0x06,'docx':0x07,'js':0x08,'java':0x09,'dll':0x0a}
        self.extension_types_coverter = {0x00:'txt',0x01:'py',0x02:'png',0x03:'jpg',0x04:'jpeg',0x05:'pdf',0x06:'gif',0x07:'docx',0x08:'js',0x09:'java',0x0a:'dll'}
        self.__resp__ = {0x01:"EoP not found",0x02:"EoP wrong position",0x03:"payLoadSize != realPayloadSize",0x04:"Wrong package number",0x05:"Success",0x06:"Timeout",0xff:None}
        self.extension = None
        self.filesize = None
        self.packageNumber = 1
        self.numberOfPackages = 1
        self.response = 0xff
        self.package = None

    def mountHead(self):
        self.head = int.to_bytes(4, self.packageNumber)
        self.head += self.response
        self.head += int.to_bytes(4,self.numberOfPackages)
        try:
            self.head += int.to_bytes(1, self.extension_types[self.extension])
        except:
            self.head += bytes([0xff])
    def startThreads(self):
        self.comm.enable()

class Client(Master):
    '''
    Classe que irá mandar um arquivo, mas também deve receber a agir de acordo com a resposta
    '''
    # def __init__(self, filepath, serialport):
    def __init__(self, filepath, serialport, comm):
        # super().__init__(serialport)
        super().__init__(serialport, comm)
        self.extension = str(filepath)[0].split('.')[-1]
        with open(filepath, "rb") as arquivo:
            self.arquivo = arquivo.read()
        self.filesize = len(self.arquivo)
        self.packageNumber = 1
        self.numberOfPackages = ceil(self.filesize/128)
        self.response = 0xff

    def sendPackage(self):
        left = True
        while left:
            self.mountHead()
            builder = PackageMounter(self.head,self.arquivo,self.eop)
            self.leftOvers = builder.getLeftovers()
            self.package = builder.getPackage()
            if self.package != None:
                self.comm.sendData(self.package)
                self.readResponse()
                print(self.__resp__[self.response])
                if self.__resp__[self.response] != "Success":
                    break
                if self.leftOvers != None:
                    self.package = self.leftOvers
                    self.leftOvers = None
                else:
                    left = False
            else:
                print('[ERRO] empty package')
                break
            self.packageNumber += 1
        print("Send Done...")
        
    def readResponse(self):
        while self.comm.rx.getIsEmpty():
            "Waiting response..."
            pass
        resp, nRx = self.comm.getData(12)
        size = int.from_bytes(resp[-1])
        self.response = resp[4]
        resto, nRx2 = self.comm.getData(size+4)
        if not (resto[-4]+resto[-3]+resto[-2]+resto[-1] == self.eop):
            print("[ERROR] EoP não encontrado")
        
    def setFile(self, filepath):
        with open(filepath, "rb") as arquivo:
            self.arquivo = arquivo.read()
        return None


class Server(Master):
    # def __init__(self,serialport):
    def __init__(self,serialport, comm):
        # super().__init__(serialport)
        super().__init__(serialport, comm)
        self.mensagem = None
        self.packageNumber = 1
    
    def start(self):
        while self.packageNumber <= self.numberOfPackages:
            while self.comm.rx.getIsEmpty:
                print("Waiting Data...")
                pass
            self.package, nRx = self.comm.getData(12)
            size = int.from_bytes(self.package[-1])
            pay_eop, nRx2 = self.comm.getData(size+4)
            print("Tamanho " + str(nRx + nRx2))
            destroy = PackageDismounter(pay_eop, size)
            self.response = destroy.getResponse()
            self.packageNumber = destroy.getPackageNumber
            self.numberOfPackages = destroy.getTotalOfPackages
            self.mensagem += destroy.getMessage
            print(destroy.getMessage)
            self.comm.sendData(self.response)
        self.extension = destroy.getExtencin
        self.mensagem += "."+self.extension_types_coverter[self.extension]
        with open("Arquivo_Enviado", "wb") as arq:
            arq.write(self.mensagem)