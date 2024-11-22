import socket
import time
import random

# Função para calcular o checksum
def calculate_checksum(message):
    return sum(ord(c) for c in message) % 256

# Função para introduzir erro em um pacote
def introduce_error(message):
    if len(message) > 1:
        index = random.randint(0, len(message) - 1)
        message = message[:index] + '?' + message[index + 1:]
    return message

def client_program():
    host = socket.gethostname()
    port = 5000

    client_socket = socket.socket()
    client_socket.connect((host, port))

    # Solicita o protocolo de retransmissão
    protocol = input("Escolha o protocolo (1 = Go-Back-N, 2 = Repetição Seletiva): ")
    client_socket.send(protocol.encode())

    # Define o tamanho da janela (obtido do servidor)
    window_size = int(client_socket.recv(1024).decode())
    print(f"Tamanho da janela recebido do servidor: {window_size}")

    while True:
        mode = input("Escolha o modo de envio (1 = único pacote, 2 = rajada de pacotes): ")

        if mode == '1':
            message = input(" -> ")
            corrupt = input("Deseja corromper o pacote? (s/n): ")
            sequence_number = 1  # Define o número de sequência para pacote único
            checksum = calculate_checksum(message)

            if corrupt.lower() == 's':
                message = introduce_error(message)
                print(f"Enviado: {message}")

            packet = f"{sequence_number}|{message}|{checksum}"
            start_time = time.time()  # Inicia o temporizador

            client_socket.send(packet.encode())

            try:
                client_socket.settimeout(2)  # Limite de 2 segundos
                ack = client_socket.recv(1024).decode()
                elapsed_time = time.time() - start_time
                print(f"Confirmação do servidor: {ack} (RTT: {elapsed_time:.3f}s)\n")
            except socket.timeout:
                print("Tempo de espera esgotado. Pacote será retransmitido.\n")
                client_socket.send(packet.encode())  # Retransmissão

        elif mode == '2':
            num_packets = int(input("Digite o número de pacotes para enviar em rajada: "))
            interval = float(input("Digite o intervalo entre pacotes (em segundos): "))
            packets_to_corrupt = input("Digite os números dos pacotes a serem corrompidos (ex: 1,3): ")
            packets_to_corrupt = [int(x.strip()) for x in packets_to_corrupt.split(',')]

            for i in range(num_packets):
                message = input(f"Pacote {i + 1} -> ")
                sequence_number = i + 1
                checksum = calculate_checksum(message)

                if (i + 1) in packets_to_corrupt:
                    message = introduce_error(message)

                packet = f"{sequence_number}|{message}|{checksum}"
                start_time = time.time()  # Inicia o temporizador

                client_socket.send(packet.encode())

                try:
                    client_socket.settimeout(2)  # Limite de 2 segundos
                    ack = client_socket.recv(1024).decode()
                    elapsed_time = time.time() - start_time
                    print(f"Confirmação do servidor: {ack} (RTT: {elapsed_time:.3f}s)\n")
                except socket.timeout:
                    print(f"Tempo de espera esgotado para o pacote {sequence_number}. Retransmitindo...\n")
                    client_socket.send(packet.encode())  # Retransmissão

                time.sleep(interval)

        else:
            print("Modo inválido. Por favor, escolha 1 ou 2.")

        exit_option = input("Deseja encerrar? (s/n): ")
        if exit_option.lower() == 's':
            client_socket.send("bye".encode())
            break

    client_socket.close()

if __name__ == '__main__':
    client_program()

