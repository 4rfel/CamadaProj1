
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Aplicação 
####################################################

print("comecou")

from enlace import *
import time
import binascii
import tkinter as tk
from tkinter import filedialog



# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)

serialName = "COM6"                  # Windows(variacao de)
print("abriu com")

def main():
    # Inicializa enlace ... variavel com possui todos os metodos e propriedades do enlace, que funciona em threading
    com = enlace(serialName) # repare que o metodo construtor recebe um string (nome)
    # Ativa comunicacao
    com.enable()

    # Log
    print("-------------------------")
    print("Comunicação inicializada")
    print("  porta : {}".format(com.fisica.name))
    print("-------------------------")

    # Carrega dados
    print ("gerando dados para transmissao :")
  
      #no exemplo estamos gerando uma lista de bytes ou dois bytes concatenados
    
    #exemplo 1
    #ListTxBuffer =list()
    #for x in range(1,10):
    #    ListTxBuffer.append(x)
    #txBuffer = bytes(ListTxBuffer)

    root = tk.Tk()
    root.withdraw()
    
    filepath = filedialog.askopenfilename()

    #exemplo2
    with open(str(filepath),"rb") as logo:
        txBuffer = logo.read()
    #txBuffer = bytes("Mas vai pra puta que o pariu",'utf-8')
    print(txBuffer)

    txLen = len(txBuffer)
    txLen = (txLen).to_bytes(2, byteorder='big')

    txBuffer = txLen + txBuffer

    # Transmite dado
#    print("tentado transmitir .... {} bytes".format(txLen))

    t = time.time()
    com.sendData(txBuffer)

    # espera o fim da transmissão
    #while(com.tx.getIsBussy()):
    #    pass
    
    
    # Atualiza dados da transmissão
    txSize = com.tx.getStatus()
#    print ("Transmitido       {} bytes ".format(txSize))


    # Faz a recepção dos dados
#    print ("Recebendo dados .... ")
    
    #repare que o tamanho da mensagem a ser lida é conhecida! 
    rxBuffer, nRx = com.getData(2)
    t1 = time.time() - t
    lido = int.from_bytes(rxBuffer, 'big')
    
    print("tempo: " + str(t1))
    print("Lida: "+ str(lido))
    print("velocidade: " + str(lido/t1))

    with open("byterate.txt", "a") as text:
        text.write("path: {3}\ntempo total: {0} \ntamanho img: {1} \nbyterate: {2} \n --------------x---------------".format(t1, lido, lido/t1, filepath))

    # log
    print ("{} bytes ".format(nRx))
    
    print (rxBuffer)

    

    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    for e in range(10):
        main()
