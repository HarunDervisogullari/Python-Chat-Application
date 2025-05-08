import socket
import threading

HOST = '192.168.136.1'
PORT = 9090
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))

server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        try:
            client.send(message)
        except:
            handle_disconnection(client)

def handle_disconnection(client):
    if client in clients:
        index = clients.index(client)
        nickname = nicknames[index]
        clients.remove(client)
        nicknames.remove(nickname)
        broadcast(f"{nickname} has left the chat.\n".encode('utf-8'))
        client.close()
        broadcast_users()

def broadcast_users():
    user_list = ','.join(nicknames)
    print(f"Broadcasting user list: {user_list}")
    for client in clients:
        try:
            client.send(f"USERS {user_list}".encode('utf-8'))
        except:
            handle_disconnection(client)

def handle(client):
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.startswith('EXIT'):
                handle_disconnection(client)
                break
            elif message == "USERS":
                broadcast_users()
            else:
                print(f"{nicknames[clients.index(client)]} says {message}")
                broadcast(message.encode('utf-8'))
        except:
            handle_disconnection(client)
            break

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}!")

        client.send("NICK".encode('utf-8'))
        nickname = client.recv(1024).decode('utf-8')
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nickname of the client is {nickname}")
        broadcast(f"{nickname} connected to the server!\n".encode('utf-8'))
        broadcast_users()
        client.send("Connected to the server".encode('utf-8')) 

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server running...")
receive()
