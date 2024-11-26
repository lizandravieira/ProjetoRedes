# 💻Projeto: Aplicação Cliente-Servidor
## **Descrição do Projeto**
>Este projeto é uma aplicação cliente-servidor que simula o transporte confiável de dados na camada de aplicação. O sistema lida com perda e corrupção de pacotes, implementa controle de fluxo e controle de congestionamento, e suporta protocolos como Go-Back-N e Repetição Seletiva.

## **Desenvolvedores**
<p><a href="https://github.com/alecct812">Alec Theotônio</a> 
<p><a href="https://github.com/TheEuri">Eurivaldo Vasconcelos</a> 
<p><a href="https://github.com/Felipeserpa01">Felipe Serpa</a> 
<p><a href="https://github.com/lizandravieira">Lizandra Vieira</a> 
<p><a href="https://github.com/Ferraz27">Lucas Ferraz</a> 
<p><a href="https://github.com/Zabbak">Lucas Kabbaz</a> 

## **Funcionalidades**
### 👨🏻‍💻**Cliente**
- Envio de pacotes:
  - Suporte para envio de pacotes únicos ou em rajada.
  - Introdução manual de erros de integridade nos pacotes enviados.
- Temporizador:
  - Retransmissão de pacotes caso o servidor não responda dentro do tempo limite.
- Controle de fluxo:
  - Janela deslizante ajustável conforme informado pelo servidor.
- Protocolos de retransmissão:
  - Suporte para Go-Back-N e Repetição Seletiva, negociado no início da conexão.

### 🖥️**Servidor**
- Processamento de pacotes:
  - Valida número de sequência, integridade (checksum) e conteúdo dos pacotes.
- Simulação de falhas:
  - Perdas de pacotes (20%) e erros em confirmações (30%).
- Controle de fluxo:
  - Janela de recepção dinâmica, informada ao cliente.
- Respostas ao cliente:
  - Envio de ACK (confirmação positiva) e NACK (confirmação negativa).

- Detalhes adicionais:
  - O envio do pacote possui um mecanismo de tratamento para o tamanho da mensagem. Se o pacote exceder o limite de 5 caracteres, os caracteres além desse limite são descartados. Isso significa que apenas os primeiros 5 caracteres da mensagem serão enviados, enquanto o restante será ignorado.
  - Esse comportamento é implementado para prevenir o estouro do buffer, que pode ocorrer quando uma quantidade de dados maior do que a capacidade esperada é processada. Ao limitar a mensagem a 5 caracteres e descartar o excesso, o sistema garante que o buffer será utilizado de forma segura, evitando problemas como falhas ou corrupção de dados devido a sobrecarga.
    
  ![image](https://github.com/user-attachments/assets/546fecb3-65bb-4fcd-b44a-5b97b22453f9)

---

## **Protocolo de Comunicação**
### Estrutura de um Pacote
- **sequence_number**: Número de sequência do pacote.
- **message**: Dados enviados no pacote.
- **checksum**: Soma de verificação para validar a integridade.

### Estrutura de Respostas do Servidor
- **ACK**: Indica sucesso no recebimento do pacote.
- **NACK**: Indica erro ou corrupção no pacote.

---

## **Como Executar**
### **1. Clonar o Repositório**
```bash
git clone https://github.com/lizandravieira/ProjetoRedes
```
### **2. Iniciar Servidor**
- Abra um terminal ou prompt de comando.
- Navegue até o diretório do projeto.
- Execute o servidor:
```bash
python socket_server.py
```
- O servidor ficará aguardando conexões, exibindo a mensagem:
```bash
Aguardando conexão...
```
### **3. Iniciar o Cliente**
- Em outro terminal ou prompt de comando.
- Navegue até o diretório do projeto.
- Execute o cliente:
```bash
python socket_client.py
```
### **4. Escolher Configurações no Cliente**
- O cliente solicitará as seguintes entradas:
   - Protocolo de Retransmissão:
     - Digite 1 para Go-Back-N ou 2 para Repetição Seletiva.
   - Modo de Envio:
     - Digite 1 para enviar um único pacote.
     - Digite 2 para enviar uma rajada de pacotes.
   - Corromper Pacotes:
     - Para pacotes individuais, o cliente perguntará se deseja corrompê-los (s para sim ou n para não).
     - Para rajadas, você pode especificar quais pacotes corromper (exemplo: 1,3,5).

### **5. Logs no Servidor e Cliente**
- O servidor exibirá logs detalhados sobre pacotes recebidos, perdas simuladas e confirmações enviadas.
  - O cliente exibirá mensagens sobre:
    - Envio de pacotes.
    - Recebimento de confirmações (ACK/NACK).
    - Retransmissões em caso de perda.

### **6.Encerrar a Conexão**
-  Para encerrar a conexão:
  - No cliente, digite s quando for perguntado:
  ```bash
  Deseja encerrar? (s/n):
  ```
  - O servidor registrará a desconexão do cliente e finalizará a conexão.
