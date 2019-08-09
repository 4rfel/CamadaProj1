
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

import cv2


print("OpenCV Version : %s " % cv2.__version__)

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH,320/2)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240/2)

ret, frame = cap.read()

cap.release()

cv2.imwrite("foto_original.png", frame)



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
    print ("gerando dados para transmissao :")
  
      #no exemplo estamos gerando uma lista de bytes ou dois bytes concatenados
    
    #exemplo 1
    #ListTxBuffer =list()
    #for x in range(1,10):
    #    ListTxBuffer.append(x)
    #txBuffer = bytes(ListTxBuffer)
    
    #exemplo2

    # txBuffer = bytes([3]) + bytes([3]) + bytes([3]) + bytes([3]) + bytes([3]) + bytes([3]) + bytes([3]) + bytes([3]) 
    with open("aaaa.png", "rb") as foto:
      txBuffer = foto.read()
    txLen    = len(txBuffer)
    print(txLen)

    #Transmite tamanho da foto
    aaa = bytes(str(txLen), "utf-8")
    print("tamanho do txLen em bytes {}".format(len(aaa)))
    start_time = time.time()
    com.sendData(aaa)


    # Transmite dado
    time.sleep(0.01)
    print("tentado transmitir .... {} bytes".format(txLen))
    com.sendData(txBuffer)

    # espera o fim da transmissão
    #while(com.tx.getIsBussy()):
    #    pass
    
    
    # Atualiza dados da transmissão
    txSize = com.tx.getStatus()
    print ("Transmitido       {} bytes ".format(txSize))

    # Faz a recepção dos dados
    print ("Recebendo dados .... ")
    
    #repare que o tamanho da mensagem a ser lida é conhecida!     
    rxBuffer, nRx = com.getData(txLen) #rxBuffer tamanho recebido pelo jao
    
    # with open("foto_copiada.png", "wb") as f:
    #   f.write(rxBuffer)
    

    # log
    # print ("Lido              {} bytes ".format(nRx))
    
    # print (rxBuffer)
    size_jao = int(rxBuffer)
    if (size_jao == txLen):
      elapsed_time = time.time() - start_time
      print("Deu bom, os 2 tem o tamanho de {0} \no tempo total foi de {1} com um byterate de {2} t/bytes".format(size_jao, elapsed_time, elapsed_time/txLen))
    else:
      print("Não deu bom, tamanho transmitido {0}, tamanho recebido {1}".format(txLen, size_jao))

    # # Encerra comunicação
    # print("-------------------------")
    # print("Comunicação encerrada")
    # print("-------------------------")
    com.disable()

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
