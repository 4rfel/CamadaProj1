
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
#Carareto
#17/02/2018
#  Aplicação 
####################################################


from enlace import *
import binascii

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM4"                  # Windows(variacao de)


def main():
    # Inicializa enlace ... variavel com possui todos os metodos e propriedades do enlace, que funciona em threading
    com = enlace(serialName) # repare que o metodo construtor recebe um string (nome)
    # Ativa comunicacao
    com.enable()

    # Log
    # print("-------------------------")
    print("Comunicação inicializada")
    # print("  porta : {}".format(com.fisica.name))
    # print("-------------------------")

    # # Carrega dados
    # print ("gerando dados para transmissao :")
  
      #no exemplo estamos gerando uma lista de bytes ou dois bytes concatenados
      
    #exemplo 1
    #ListTxBuffer =list()
    #for x in range(1,10):
    #    ListTxBuffer.append(x)
    #txBuffer = bytes(ListTxBuffer)
    
    #exemplo2
    # txBuffer = bytes([2]) + bytes([3])+ bytes("teste", 'utf-8')
    
    
    # txLen    = len(txBuffer)
    # print(txLen)

    # Transmite dado
    # print("tentado transmitir .... {} bytes".format(txLen))
    # com.sendData(txBuffer)

    # espera o fim da transmissão
    # while(com.tx.getIsBussy()):
    #    pass
    
    
    # Atualiza dados da transmissão
    txSize = com.tx.getStatus()
    # print ("Transmitido       {} bytes ".format(txSize))

    # # Faz a recepção dos dados
    # print ("Recebendo dados .... ")
    
    #repare que o tamanho da mensagem a ser lida é conhecida! 

    txLen, nRxLen = com.getData(2)
    txLen = int.from_bytes(txLen, 'big')

    # print("txLen é             :" + str(txLen))

    rxBuffer, nRx = com.getData(txLen) 

    # log
    # print ("Lido              {} bytes ".format(nRx))
    
    # print (rxBuffer)
    com.sendData(nRx.to_bytes(2, "big"))


    with open("received_image" + str(testNumber) + ".png", "wb") as image:
        image.write(rxBuffer)

    

    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("-------------------------")
    com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
testNumber = 0
if __name__ == "__main__":
    # for e in range(10):
        # main()
        # testNumber += 1
    main()
