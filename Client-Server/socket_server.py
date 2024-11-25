import socket
import random
import time

# Função para calcular o checksum
def calculate_checksum(message):
    return sum(ord(c) for c in message) % 256

# Função para introduzir erro na confirmação (simulando falha na comunicação)
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

    # Negociação do protocolo com o cliente
    protocol = conn.recv(1024).decode()
    protocol_name = "Go-Back-N" if protocol == '1' else "Repetição Seletiva"
    print(f"Protocolo escolhido pelo cliente: {protocol_name}")

    # Define o tamanho da janela
    window_size = 5
    conn.send(str(window_size).encode())

    accumulated_responses = []
    expected_packets = 0
    is_burst_mode = False
    packets_received = 0
    last_ack_sent = 0
    received_packets = {}

    while True:
        try:
            conn.settimeout(10)
            data = conn.recv(1024).decode()
            
            if not data or data.lower().strip() == 'bye':
                print("Conexão encerrada pelo cliente.")
                break

            print(f"Dado recebido do cliente: {data}")

            # Se é o início de uma rajada, extraia o número de pacotes esperados
            if data.startswith("BURST:"):
                expected_packets = int(data.split(":")[1])
                is_burst_mode = True
                packets_received = 0
                accumulated_responses = []
                received_packets = {}
                print(f"Iniciando modo rajada. Esperando {expected_packets} pacotes.")
                continue

            # Processa o pacote recebido
            if random.random() < 0.2:  # 20% de chance de "perder" o pacote
                print("Pacote perdido (simulação). Nenhum processamento realizado.")
                if is_burst_mode:
                    packets_received += 1
                continue

            try:
                sequence_number, message, received_checksum = data.split('|')
                sequence_number = int(sequence_number)
                print(f"Processando pacote {sequence_number}")
            except ValueError as e:
                print(f"Erro ao processar dados: {e}")
                continue

            # Verifica corrupção no pacote
            if '?' in message:
                print(f"Erro: Mensagem corrompida detectada! Sequência {sequence_number}")
                response = f"NACK|{sequence_number}"
            else:
                # Calcula e valida o checksum
                calculated_checksum = calculate_checksum(message)
                if int(received_checksum) != calculated_checksum:
                    print(f"Erro de integridade detectado! Sequência {sequence_number}")
                    response = f"NACK|{sequence_number}"
                else:
                    print(f"Pacote {sequence_number} recebido com sucesso: {message}")
                    response = f"ACK|{sequence_number}"
                    received_packets[sequence_number] = message
                    if protocol == '1':  # Go-Back-N
                        if sequence_number == last_ack_sent + 1:
                            last_ack_sent = sequence_number
                        else:
                            response = f"ACK|{last_ack_sent}"

            if is_burst_mode:
                accumulated_responses.append(response)
                packets_received += 1
                
                # Se recebeu todos os pacotes da rajada, envia todas as respostas
                if packets_received >= expected_packets:
                    combined_response = ";".join(accumulated_responses)
                    conn.send(combined_response.encode())
                    print(f"Enviando respostas acumuladas: {combined_response}")
                    is_burst_mode = False
                    accumulated_responses = []
            else:
                # Modo normal (pacote único)
                response = introduce_error(response)
                conn.send(response.encode())

        except socket.timeout:
            if is_burst_mode and accumulated_responses:
                # Envia as respostas acumuladas mesmo em caso de timeout
                combined_response = ";".join(accumulated_responses)
                conn.send(combined_response.encode())
                print(f"Enviando respostas acumuladas após timeout: {combined_response}")
                is_burst_mode = False
                accumulated_responses = []
            else:
                # Envia ACK para o último pacote recebido em ordem
                if last_ack_sent > 0:
                    response = f"ACK|{last_ack_sent}"
                    response = introduce_error(response)
                    conn.send(response.encode())
                    print(f"Reenviando último ACK: {response}")
                print("Tempo de espera esgotado para receber dados.")
            continue

        except ConnectionResetError as e:
            print(f"Conexão encerrada pelo cliente: {e}")
            break

        except Exception as e:
            print(f"Erro na recepção de pacotes: {e}")
            continue

    conn.close()

if __name__ == '__main__':
    server_program()