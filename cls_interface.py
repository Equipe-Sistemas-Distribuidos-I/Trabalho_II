import devices_pb2
from socket import *
# import threading
from constants import *


class cls():
    def __init__(self , server_Name = gethostbyname(gethostname()) , skt_Port = 50151 , max_conections = 5) -> None:
        self.skt_Server  = socket(AF_INET , SOCK_STREAM)
        self.skt_Port = skt_Port
        self.skt_Server.bind((server_Name , self.skt_Port))
        self.server_Name = server_Name
        # self.skt_Server.listen(max_conections)

    def prompt(self ,server_Name = gethostbyname(gethostname()) ,  port_to_connect = 50051):
        # client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.skt_Server.connect(( server_Name , port_to_connect ))

        screen_msg = "Tipos de Dispositivos Disponíveis :\n\n1-ar_condicionado\n2-lampada\n3-geladeira\n \n"
        
        msg3 = "\n5-close_connection\n6-close\n7-gateway_find_devices"
        # screen_msg += msg2 + msg3
        while True:
            print(screen_msg)
            # print("")
            device_type = ""
            while True :
                device_type = input("Digite o número do tipo de dispositivo que você quer interagir : ").strip().lower()
                if device_type.isnumeric():
                    device_type = int(device_type)
                    if (1 <= device_type) and (device_type <=3) :
                        break
                    else :
                        print("Digite um número dentro do range válido")
                else :
                    print("Input Inválido")
            
            dev = ""
            msg_aux = ""
            if device_type == 1 :
                dev  = "ar_condicionado"
                msg_aux = f"\n4-{dev}_temp"
            elif device_type == 2 :
                dev  = "lampada"
            elif device_type == 3 :
                dev  = "geladeira"
                msg_aux = f"\n4-{dev}_temp"

            msg2 = f"\nMétodos Disponíveis :\n\n1-{dev}_status\n2-{dev}_on\n3-{dev}_off"#
            device_name = input("Digite o nome do dispositivo que você quer interagir : ").strip()
            print(msg2 +msg_aux + msg3)
            print("Para usar alguma das funcionalidades do dispositívo digite o respectivo número ao envéz de um comando")
            comando = input("Digite um comando (cls ou clear para limpar a tela, sair para encerrar): ").strip().lower()

            if comando.isnumeric() :
                message  = devices_pb2.use_request()
                message.device_name   = device_name
                
                if device_type == 1 :
                    message.service  = "ar_condicionado"
                elif device_type == 2 :
                    message.service  = "lampada"
                elif device_type == 3 :
                    message.service  = "geladeira"
                
                else :
                    print("Dispositivo inválido")

                if   int(comando) == 1 :
                    # message.device_method = "ar_condicionado_status"
                    message.method = f"{message.service}_status"
                elif int(comando) == 2 :
                    # message.device_method = "ar_condicionado_on"
                    message.method = f"{message.service}_on"
                elif int(comando) == 3 :
                    # message.device_method = "ar_condicionado_off"
                    message.method = f"{message.service}_off"
                elif int(comando) == 4 :
                    # message.device_method = "ar_condicionado_temp"
                    message.method = f"{message.service}_temp"
                    args = ""
                    while True :
                        args  = input("Qual a nova temperatura ? : ").strip().lower()
                        if args.isnumeric():
                            break
                        else :
                            print("Input Inválido")
                    message.args = args

                elif int(comando) == 5 :
                    message.method = "close_connection"
                elif int(comando) == 6 :
                    message.method = "close"

                self.skt_Server.send(message.SerializeToString())

                response = self.skt_Server.recv(1024)
                response_handler = None

                if device_type == 1 : #"ar_condicionado"
                    response_handler = devices_pb2.ar_condicionado_info()
                elif device_type == 2 : # "lampada"
                    response_handler = devices_pb2.lampada_info()
                elif device_type == 3 : #"geladeira"
                    response_handler = devices_pb2.ar_condicionado_info()

                
                response_handler.ParseFromString(response)

                print(f"A resposta foi :\n\n {response_handler}")
            elif comando == "sair":
                break
            elif comando == "cls" and platform.system() == "Windows":
                # Limpar a tela no Windows
                subprocess.run("cls", shell=True)
            elif comando == "clear" and platform.system() != "Windows":
                # Limpar a tela em sistemas Unix-like (Linux, macOS)
                subprocess.run("clear", shell=True)
            else:
                print("Comando não reconhecido.")


        """request = devices_pb2.use_request()
        request.device_name   = "Brastemp-Eletrolux_X86"
        request.device_method = "ar_condicionado_temp"
        request.args = "2"

        request.service = "ar_condicionado"  
        request.method  = "ar_condicionado_temp"
        
        client_socket.send(request.SerializeToString())

        data = client_socket.recv(1024)
        response = ar_condicionado_pb2.ar_condicionado_info()
        response.ParseFromString(data)"""

cmd = cls()
cmd.prompt(port_to_connect = 50051)