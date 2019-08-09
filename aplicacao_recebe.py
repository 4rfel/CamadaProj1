
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Aplicação 
####################################################

print("comecou")

from enlace_recebe import *
import time
import binascii


# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)
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
    #print ("gerando dados para transmissao :")
  
      #no exemplo estamos gerando uma lista de bytes ou dois bytes concatenados
    
    # Atualiza dados da transmissão
    #txSize = com.tx.getStatus()
    #print ("Transmitido       {} bytes ".format(txSize))
    txLen, nTx = com.getData(10)
    print("TxLen = " + str(txLen))
    print("nTx = " + str(nTx))
    # Faz a recepção dos dados
    print ("Recebendo dados .... ")
    
    #repare que o tamanho da mensagem a ser lida é conhecida! 
    rxBuffer, nRx = com.getData(int(binascii.unhexlify(txLen)))

    with open("foto_recebida.png", "wb") as foto:
      foto.write(rxBuffer)
    
    #Retransmitir o tamanho
    
    com.sendData(nRx)

    # log
    print ("Lido              {} bytes ".format(nRx))
    
    print (rxBuffer)

    

    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
