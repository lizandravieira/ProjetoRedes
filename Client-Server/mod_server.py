import socket
import random
import time

def calculate_checksum(message):
    return sum(ord(c) for c in message) % 256

def introduce_error(message):
    if random.random() < 0.3:  # 30% de chance de corromper a confirmação
        if len(message) > 1:
            index = random.randint(0, len(message) - 1)
            message = message[:index] + '?' + message[index + 1:]
    return message

def server_program():
    host = '127.0.0.1'
    port = 6000

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen(2)
    print("Aguardando conexão...")

    conn, address = server_socket.accept()
    print("Conexão de: " + str(address))

    protocol = conn.recv(1024).decode()
    protocol_name = "Go-Back-N" if protocol == '1' else "Repetição Seletiva"
    print(f"Protocolo escolhido pelo cliente: {protocol_name}")

    window_size = 5
    conn.send(str(window_size).encode())

    accumulated_responses = []
    expected_packets = 0
    is_burst_mode = False
    received_packets = {}

    # Variáveis específicas para Go-Back-N
    expected_seq_num = 1
    last_ack_sent = 0

    while True:
        try:
            conn.settimeout(10)
            data = conn.recv(1024).decode()

            if not data or data.lower().strip() == 'bye':
                print("Conexão encerrada pelo cliente.")
                break

            print(f"Dado recebido do cliente: {data}")

            # Processamento de dados e pacotes
            if data.startswith("BURST:"):
                expected_packets = int(data.split(":")[1])
                is_burst_mode = True
                accumulated_responses = []
                received_packets = {}
                expected_seq_num = 1
                last_ack_sent = 0
                print(f"Iniciando modo rajada. Esperando {expected_packets} pacotes.")
                continue

            # Simulação de perda de pacotes
            if random.random() < 0.2:
                print("Pacote perdido (simulação)")
                continue

            # Processar pacotes e validar
            try:
                sequence_number, message, received_checksum = data.split('|')
                sequence_number = int(sequence_number)
                received_checksum = int(received_checksum)
                print(f"Processando pacote {sequence_number}")
            except ValueError as e:
                print(f"Erro ao processar dados: {e}")
                continue

            is_corrupt = '?' in message
            is_valid_checksum = received_checksum == calculate_checksum(message)
            is_valid_packet = not is_corrupt and is_valid_checksum

            # Go-Back-N
            if protocol == '1':
                if sequence_number == expected_seq_num and is_valid_packet:
                    print(f"Pacote {sequence_number} recebido em ordem e íntegro")
                    last_ack_sent = sequence_number
                    expected_seq_num += 1
                    received_packets[sequence_number] = message
                else:
                    print(f"Pacote {sequence_number} descartado (fora de ordem ou corrompido)")
                response = f"ACK|{last_ack_sent}"
            else:
                # Repetição Seletiva
                pass  # Implementação futura para outros protocolos

            # Garantir resposta válida
            if not response.startswith("ACK|") and not response.startswith("NACK|"):
                print(f"Corrigindo resposta inválida para ACK|{last_ack_sent}")
                response = f"ACK|{last_ack_sent}"  # Força formato correto

            # Enviar resposta acumulada ou individual
            if is_burst_mode:
                accumulated_responses.append(response)
                if len(received_packets) >= expected_packets:
                    combined_response = ";".join(set(accumulated_responses))
                    conn.send(combined_response.encode())
                    print(f"Enviando respostas acumuladas: {combined_response}")
                    is_burst_mode = False
                    accumulated_responses = []
            else:
                conn.send(f"{response};".encode())  # Adiciona delimitador ;
                print(f"Enviando resposta: {response}")

        except socket.timeout:
            # Enviar respostas acumuladas durante rajada em timeout
            if is_burst_mode and accumulated_responses:
                combined_response = ";".join(set(accumulated_responses))
                conn.send(combined_response.encode())
                print(f"Timeout - Enviando respostas acumuladas: {combined_response}")
                is_burst_mode = False
                accumulated_responses = []
            continue

    conn.close()

if __name__ == '__main__':
    server_program()