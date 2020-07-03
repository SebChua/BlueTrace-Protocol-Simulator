import sys
import socket
from DataManager import DataManager

def handle_login(credentials):
    # Open credentials.txt and check for any matching lines
    credential_file = open('credentials.txt', 'r')
    print('Credential received:', credentials)
    for valid_credential in credential_file:
        username, password = valid_credential.split()
        if username == credentials['username'] and password == credentials['password']:
            # Found a registered user
            print('FOUND A VALID USER')
            print(valid_credential)
            return True
    print('No valid user found')
    credential_file.close()
    return False

if len(sys.argv) != 3:
    print('Usage: {} server_port block_duration'.format(sys.argv[0]))
    exit()

server_IP = 'localhost'
server_port = int(sys.argv[1])
block_duration = int(sys.argv[2])   # Duration (seconds) user will be blocked after 3 unsuccessful login attempts

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((server_IP, server_port))
server_socket.listen(1)
print('Server listening for connections.')

client_socket, address = server_socket.accept()
received_data = client_socket.recv(4096)
if received_data:
    credentials = DataManager.decode_object(received_data)
    handle_login(credentials)

client_socket.close()
