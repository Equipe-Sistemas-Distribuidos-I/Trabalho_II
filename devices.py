import devices_pb2
from socket import *
import threading
from abc import ABC, abstractmethod
from constants import *
import struct
import time


class device_interface(ABC):

    @abstractmethod
    def handle_request(self , connection , addr):
        pass

"""OS DISPOSITIVOS SERÃO TODOS SERVIDORES , ENQUANTO O GATEWAY É TANTO CLIENTE DOS DISPOSITIVOS , QUANTO SERVIDOR
DE QUEM QUEIRA SE CONECTAR AO SISTEMA SERVINDO COMO A INTERFACE COM O MUNDO EXTERNO"""


class ar_condicionado(device_interface):

    def __init__(self , name : str ="Brastemp_Eletrolux" , on: bool = True, temperature : int = 20  ,
                 server_Name = gethostbyname(gethostname()) , server_Port = 50051  ) -> None:
        super(ar_condicionado , self).__init__()
        self.name = name
        self.temperature = temperature
        self.on = on
        
        self.server_Port = server_Port
        self.skt_Server  = socket( AF_INET , SOCK_STREAM )
        self.skt_Server.bind(( server_Name , server_Port ))
        self.skt_Server.listen(5)
        
        
        print("Server Ligado ", server_Name )
    
    def tcp_connect(self , timeout = 6):
        client , addr = None , None
        print("ar_condicionado aberto a novas conexões TCP")
        while True :
            try :
                self.skt_Server.settimeout(timeout)

                client , addr = self.skt_Server.accept()

                mp = threading.Thread(target = self.handle_request , args=(client, addr))
                mp.start()

            except error as e:
                # Tratamento de exceção para liberar a thread em caso de interrupção
                print("tempo de espera por novas conexões em ar_condicionado encerrado ")
                
                return
            

    def send_info_2_multicast(self , timer = 10):
        # Criação de um socket UDP
        sock = socket( AF_INET , SOCK_DGRAM , IPPROTO_UDP )

        # Vincula o socket a um endereço e porta local
        # server_address = ("", port )
        # sock.bind( server_address )

        # Configura o socket para enviar dados para o grupo multicast
        group = inet_aton( multicast_group )
        mreq = struct.pack( "4sL", group , INADDR_ANY )
        sock.setsockopt( IPPROTO_IP , IP_ADD_MEMBERSHIP, mreq )
        # sock.setsockopt( IPPROTO_IP , IP_MULTICAST_TTL , 8 )
        
        try:
            print("O dispositivo iniciou a tentativa de estabelecer conecção via multicast e permanecerá tentando pelos próximos 1 minuto")
            # message = f"{self.server_Port} , ar_condicionado , {self.name}"
            message = devices_pb2.device_discover()
            message.name = self.name
            message.port = self.server_Port
            message.device_type = "ar_condicionado"

            start_time = time.time()
            while True:
                
                sock.sendto(message.SerializeToString() , (multicast_group, port))
                time.sleep(1)
                if (time.time() - start_time) > timer :
                    break
            print("Servidor multicast encerrado.")
        except KeyboardInterrupt:
            print("Servidor multicast encerrado.")
        finally:
            sock.close()
    def conect_in_localhost_devices(self , timer = 4):
        
        self.exit_thread = False
        td1 = threading.Thread(target= self.send_info_2_multicast , args=(timer,))
        td1.start()

        td2 = threading.Thread(target= self.tcp_connect , args=(timer,))
        td2.start()


    def handle_request(self , connection , addr):
        print("[NOVA Conexão em..  ar_condicionado ]")

        while True :
            data = connection.recv(1024)
            if data :

                request = devices_pb2.info_request()
                request.ParseFromString(data)

                # Roteie a mensagem com base nas informações do cabeçalho
                
                if  request.service  == "ar_condicionado" and request.method == "ar_condicionado_status":
                    response = devices_pb2.ar_condicionado_info()
                    response.on =  self.on
                    response.temperature =  self.temperature

                elif request.service == "ar_condicionado" and request.method == "ar_condicionado_on"  :
                    self.on = True
                    response = devices_pb2.ar_condicionado_info()
                    response.on =  self.on
                    response.temperature =  self.temperature
                elif request.service == "ar_condicionado" and request.method == "ar_condicionado_off" :
                    self.on = False
                    response = devices_pb2.ar_condicionado_info()
                    response.on =  self.on
                    response.temperature =  self.temperature
                elif request.service == "ar_condicionado" and request.method == "ar_condicionado_temp" :
                    self.temperature = request.new_temp
                    response = devices_pb2.ar_condicionado_info()
                    response.on =  self.on
                    response.temperature =  self.temperature
                elif request.service == "ar_condicionado" and request.method == "close_connection" :
                    connection.close()
                    return
                else:
                    print("Serviço ou método desconhecido")

                # f"Hello, {request.name}!The ar condicionado {request.name} is on now ."
                
                connection.send(response.SerializeToString())
                # connection.close()
                # return

    def __str__(self) -> str:
        return f"ar_condicionado() : {self.name} , temperature : {self.temperature} , on : {self.on}"
    

class lampada(device_interface):

    def __init__(self , name : str ="INTELBRAS" , on: bool = True,
                 server_Name = gethostbyname(gethostname()) , server_Port = 51050  ) -> None:
        super(lampada , self).__init__()
        self.name = name
        self.on = on
        
        self.server_Port = server_Port
        self.skt_Server  = socket( AF_INET , SOCK_STREAM )
        self.skt_Server.bind(( server_Name , server_Port ))
        self.skt_Server.listen(5)
        
        
        print("Server Ligado ", server_Name )
    
    def tcp_connect(self , timeout = 6):
        client , addr = None , None
        print("lampada aberto a novas conexões TCP")
        while True :
            try :
                self.skt_Server.settimeout(timeout)

                client , addr = self.skt_Server.accept()

                mp = threading.Thread(target = self.handle_request , args=(client, addr))
                mp.start()

            except error as e:
                # Tratamento de exceção para liberar a thread em caso de interrupção
                print("tempo de espera por novas conexões em ar_condicionado encerrado ")
                
                return
            

    def send_info_2_multicast(self , timer = 10):
        # Criação de um socket UDP
        sock = socket( AF_INET , SOCK_DGRAM , IPPROTO_UDP )

        # Vincula o socket a um endereço e porta local
        # server_address = ("", port )
        # sock.bind( server_address )

        # Configura o socket para enviar dados para o grupo multicast
        group = inet_aton( multicast_group )
        mreq = struct.pack( "4sL", group , INADDR_ANY )
        sock.setsockopt( IPPROTO_IP , IP_ADD_MEMBERSHIP, mreq )
        # sock.setsockopt( IPPROTO_IP , IP_MULTICAST_TTL , 8 )
        
        try:
            print("O dispositivo iniciou a tentativa de estabelecer conecção via multicast e permanecerá tentando pelos próximos 1 minuto")
            # message = f"{self.server_Port} , ar_condicionado , {self.name}"
            message = devices_pb2.device_discover()
            message.name = self.name
            message.port = self.server_Port
            message.device_type = "lampada"

            start_time = time.time()
            while True:
                
                sock.sendto(message.SerializeToString() , (multicast_group, port))
                time.sleep(1)
                if (time.time() - start_time) > timer :
                    break
            print("Servidor multicast encerrado.")
        except KeyboardInterrupt:
            print("Servidor multicast encerrado.")
        finally:
            sock.close()
    def conect_in_localhost_devices(self , timer = 4):
        
        self.exit_thread = False
        td1 = threading.Thread(target= self.send_info_2_multicast , args=(timer,))
        td1.start()

        td2 = threading.Thread(target= self.tcp_connect , args=(timer,))
        td2.start()


    def handle_request(self , connection , addr):
        print("[NOVA Conexão em..  lampada ]")

        while True :
            data = connection.recv(1024)
            if data :

                request = devices_pb2.info_request()
                request.ParseFromString(data)

                # Roteie a mensagem com base nas informações do cabeçalho
                
                if  request.service  == "lampada" and request.method == "lampada_status":
                    print("Entrou em lampada Status")
                    response = devices_pb2.lampada_info()
                    response.on =  self.on
                    response.name = self.name
                    # response.temperature =  self.temperature
                elif request.service == "lampada" and request.method == "lampada_on"  :
                    self.on = True
                    response = devices_pb2.lampada_info()
                    response.on =  self.on
                    response.name = self.name
                    # response.temperature =  self.temperature
                elif request.service == "lampada" and request.method == "lampada_off" :
                    print("Entrou em lampada off")
                    self.on = False
                    response = devices_pb2.lampada_info()
                    response.on =  self.on
                    response.name = self.name
                    # response.temperature =  self.temperature
                elif request.service == "lampada" and request.method == "close_connection" :
                    connection.close()
                    return
                else:
                    print("Serviço ou método desconhecido")

                # f"Hello, {request.name}!The ar condicionado {request.name} is on now ."
                
                connection.send(response.SerializeToString())
                # connection.close()
                # return

    def __str__(self) -> str:
        return f"lampada() : {self.name} ,  on : {self.on}"
    

class geladeira(device_interface):

    def __init__(self , name : str = "Consul" , on: bool = True, temperature : int = 20  ,
                 server_Name = gethostbyname(gethostname()) , server_Port = 50051  ) -> None:
        super(geladeira , self).__init__()
        self.name = name
        self.temperature = temperature
        self.on = on
        
        self.server_Port = server_Port
        self.skt_Server  = socket( AF_INET , SOCK_STREAM )
        self.skt_Server.bind(( server_Name , server_Port ))
        self.skt_Server.listen(5)
        
        
        print("Server Ligado ", server_Name )
    
    def tcp_connect(self , timeout = 6):
        client , addr = None , None
        print("geladeira aberto a novas conexões TCP")
        while True :
            try :
                self.skt_Server.settimeout(timeout)

                client , addr = self.skt_Server.accept()

                mp = threading.Thread(target = self.handle_request , args=(client, addr))
                mp.start()

            except error as e:
                # Tratamento de exceção para liberar a thread em caso de interrupção
                print("tempo de espera por novas conexões em ar_condicionado encerrado ")
                
                return
            

    def send_info_2_multicast(self , timer = 10):
        # Criação de um socket UDP
        sock = socket( AF_INET , SOCK_DGRAM , IPPROTO_UDP )

        # Vincula o socket a um endereço e porta local
        # server_address = ("", port )
        # sock.bind( server_address )

        # Configura o socket para enviar dados para o grupo multicast
        group = inet_aton( multicast_group )
        mreq = struct.pack( "4sL", group , INADDR_ANY )
        sock.setsockopt( IPPROTO_IP , IP_ADD_MEMBERSHIP, mreq )
        # sock.setsockopt( IPPROTO_IP , IP_MULTICAST_TTL , 8 )
        
        try:
            print("O dispositivo iniciou a tentativa de estabelecer conecção via multicast e permanecerá tentando pelos próximos 1 minuto")
            # message = f"{self.server_Port} , ar_condicionado , {self.name}"
            message = devices_pb2.device_discover()
            message.name = self.name
            message.port = self.server_Port
            message.device_type = "geladeira"

            start_time = time.time()
            while True:
                
                sock.sendto(message.SerializeToString() , (multicast_group, port))
                time.sleep(1)
                if (time.time() - start_time) > timer :
                    break
            print("Servidor multicast encerrado.")
        except KeyboardInterrupt:
            print("Servidor multicast encerrado.")
        finally:
            sock.close()
    def conect_in_localhost_devices(self , timer = 4):
        
        self.exit_thread = False
        td1 = threading.Thread(target= self.send_info_2_multicast , args=(timer,))
        td1.start()

        td2 = threading.Thread(target= self.tcp_connect , args=(timer,))
        td2.start()


    def handle_request(self , connection , addr):
        print("[NOVA Conexão em..  geladeira ]")

        while True :
            data = connection.recv(1024)
            if data :

                request = devices_pb2.info_request()
                request.ParseFromString(data)

                # Roteie a mensagem com base nas informações do cabeçalho
                
                if  request.service  == "geladeira" and request.method == "geladeira_status":
                    response = devices_pb2.ar_condicionado_info()
                    response.on =  self.on
                    response.temperature =  self.temperature

                elif request.service == "geladeira" and request.method == "geladeira_on"  :
                    self.on = True
                    response = devices_pb2.ar_condicionado_info()
                    response.on =  self.on
                    response.temperature =  self.temperature
                elif request.service == "geladeira" and request.method == "geladeira_off" :
                    self.on = False
                    response = devices_pb2.ar_condicionado_info()
                    response.on =  self.on
                    response.temperature =  self.temperature
                elif request.service == "geladeira" and request.method == "geladeira_temp" :
                    self.temperature = request.new_temp
                    response = devices_pb2.ar_condicionado_info()
                    response.on =  self.on
                    response.temperature =  self.temperature
                elif request.service == "geladeira" and request.method == "close_connection" :
                    connection.close()
                    return
                else:
                    print("Serviço ou método desconhecido")

                # f"Hello, {request.name}!The ar condicionado {request.name} is on now ."
                
                connection.send(response.SerializeToString())
                # connection.close()
                # return

    def __str__(self) -> str:
        return f"geladeira() : {self.name} , temperature : {self.temperature} , on : {self.on}"
    
