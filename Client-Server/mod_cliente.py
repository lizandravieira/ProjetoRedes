import socket
import time
import random

def calculate_checksum(message):
    return sum(ord(c) for c in message) % 256

def introduce_error(message):
    if len(message) > 1:
        index = random.randint(0, len(message) - 1)
        message = message[:index] + '?' + message[index + 1:]
    return message

def client_program():
    host = '127.0.0.1'
    port = 6000

    client_socket = socket.socket()
    client_socket.connect((host, port))

    protocol = input("Escolha o protocolo (1 = Go-Back-N, 2 = Repetição Seletiva): ")
    client_socket.send(protocol.encode())

    window_size = int(client_socket.recv(1024).decode())
    print(f"Tamanho da janela recebido do servidor: {window_size}")

    base = 1
    next_seq_num = 1
    packets_in_flight = {}

    while True:
        mode = input("Escolha o modo de envio (1 = único pacote, 2 = rajada de pacotes): ")

        if mode == '1':
            message = input(" -> ")
            corrupt = input("Deseja corromper o pacote? (s/n): ")
            if corrupt.lower() == 's':
                message_to_send = introduce_error(message)
                print(f"Enviado (corrompido): {message_to_send}")
            else:
                message_to_send = message
                print(f"Enviado: {message_to_send}")

            checksum = calculate_checksum(message)
            packet = f"{next_seq_num}|{message}|{checksum}"
            packets_in_flight[next_seq_num] = packet  # Armazena o pacote não corrompido

            # Envia o pacote (possivelmente corrompido)
            send_packet = f"{next_seq_num}|{message_to_send}|{checksum}"
            client_socket.send(send_packet.encode())
            start_time = time.time()

            try:
                client_socket.settimeout(5)
                ack = client_socket.recv(1024).decode().strip()
                elapsed_time = time.time() - start_time
                print(f"ACK recebido (raw): {ack}")

                if protocol == '1':  # Go-Back-N
                    if ack.startswith("ACK|"):
                        ack_parts = ack.split("|")
                        if len(ack_parts) >= 2:
                            ack_num = int(ack_parts[1])
                            print(f"ACK recebido: {ack_num} (RTT: {elapsed_time:.3f}s)")
                            if ack_num >= base:
                                base = ack_num + 1
                                next_seq_num = base
                                packets_in_flight = {seq: pkt for seq, pkt in packets_in_flight.items() if seq >= base}
                        else:
                            print(f"Formato de ACK inválido: {ack}")
                    else:
                        print(f"ACK inválido recebido: {ack}")
                else:
                    print(f"Confirmação do servidor: {ack} (RTT: {elapsed_time:.3f}s)\n")

            except socket.timeout:
                print("Timeout - Retransmitindo pacotes não confirmados")
                if protocol == '1':  # Go-Back-N
                    for seq in range(base, next_seq_num):
                        if seq in packets_in_flight:
                            print(f"[Retransmissão] Pacote {seq}: {packets_in_flight[seq]}")
                            client_socket.send(packets_in_flight[seq].encode())
                            time.sleep(0.1)

        elif mode == '2':
            num_packets = int(input("Digite o número de pacotes para enviar em rajada: "))
            interval = float(input("Digite o intervalo entre pacotes (em segundos): "))
            packets_to_corrupt_input = input("Digite os números dos pacotes a serem corrompidos (ex: 1,3): ")

            packets_to_corrupt = [int(x.strip()) for x in packets_to_corrupt_input.split(',')] if packets_to_corrupt_input else []

            client_socket.send(f"BURST:{num_packets}".encode())
            time.sleep(0.2)

            base = 1
            next_seq_num = 1
            packets_in_flight.clear()

            print("\nEnviando pacotes...")
            while base <= num_packets:
                while next_seq_num < base + window_size and next_seq_num <= num_packets:
                    message = input(f"Pacote {next_seq_num} -> ")

                    checksum = calculate_checksum(message)
                    packet = f"{next_seq_num}|{message}|{checksum}"
                    packets_in_flight[next_seq_num] = packet  # Armazena o pacote não corrompido

                    if next_seq_num in packets_to_corrupt:
                        message_to_send = introduce_error(message)
                        send_packet = f"{next_seq_num}|{message_to_send}|{checksum}"
                        print(f"Pacote {next_seq_num} corrompido: {send_packet}")
                    else:
                        send_packet = packet
                        print(f"Pacote {next_seq_num} enviado: {send_packet}")

                    client_socket.send(send_packet.encode())
                    next_seq_num += 1
                    time.sleep(interval)

                try:
                    client_socket.settimeout(10)
                    combined_acks = client_socket.recv(1024).decode().strip()
                    print(f"ACKs recebidos (raw): {combined_acks}")

                    if protocol == '1':  # Go-Back-N
                        acks = [ack.strip() for ack in combined_acks.split(";") if ack.strip()]
                        for ack in acks:
                            if ack.startswith("ACK|"):
                                ack_parts = ack.split("|")
                                if len(ack_parts) >= 2:
                                    ack_num = int(ack_parts[1])
                                    print(f"ACK recebido: {ack_num}")
                                    if ack_num >= base:
                                        base = ack_num + 1
                                        packets_in_flight = {seq: pkt for seq, pkt in packets_in_flight.items() if seq >= base}
                                else:
                                    print(f"Formato de ACK inválido: {ack}")
                except socket.timeout:
                    print("Timeout - Retransmitindo pacotes não confirmados")
                    if protocol == '1':  # Go-Back-N
                        for seq in range(base, next_seq_num):
                            if seq in packets_in_flight:
                                print(f"[Retransmissão] Pacote {seq}: {packets_in_flight[seq]}")
                                client_socket.send(packets_in_flight[seq].encode())
                                time.sleep(0.1)

        else:
            print("Modo inválido. Por favor, escolha 1 ou 2.")

        exit_option = input("Deseja encerrar? (s/n): ")
        if exit_option.lower() == 's':
            client_socket.send("bye".encode())
            break

    client_socket.close()

if __name__ == '__main__':
    client_program()