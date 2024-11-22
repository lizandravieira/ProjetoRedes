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
    host = socket.gethostname()
    port = 5000

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

    while True:
        # Dentro do bloco de processamento do pacote, antes de processar
        try:
            # Recebe o pacote
            data = conn.recv(1024).decode()

            if not data or data.lower().strip() == 'bye':
                print("Conexão encerrada pelo cliente.")
                break

            # Simula a perda de pacotes antes de qualquer processamento
            if random.random() < 0.2:  # 20% de chance de "perder" o pacote
                print("Pacote perdido (simulação). Nenhum processamento realizado.")
                continue

            # Processa o pacote apenas se ele não foi "perdido"
            sequence_number, message, received_checksum = data.split('|')

            # Verifica corrupção no pacote
            if '?' in message:
                print(f"Erro: Mensagem corrompida detectada! Sequência {sequence_number}, Mensagem: {message}")
                conn.send(f"NACK|{sequence_number}".encode())
                continue

            # Calcula e valida o checksum
            calculated_checksum = calculate_checksum(message)
            if int(received_checksum) != calculated_checksum:
                print(f"Erro de integridade detectado! Sequência {sequence_number}")
                conn.send(f"NACK|{sequence_number}".encode())
                continue

            print(f"Pacote {sequence_number} recebido com sucesso: {message} (Checksum válido)")

            # Envia confirmação (ACK) ou erro intencional na confirmação
            ack = f"ACK|{sequence_number}"
            ack = introduce_error(ack)  # Possível erro na confirmação
            conn.send(ack.encode())

        except Exception as e:
            print(f"Erro na recepção de pacotes: {e}")
            break

    conn.close()

if __name__ == '__main__':
    server_program()
