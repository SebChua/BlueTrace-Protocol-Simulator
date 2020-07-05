import sys
import socket
from DataManager import DataManager
from server_helpers.LoginManager import LoginStatus

MAX_DELAY = 5

if len(sys.argv) != 4:
    print('Usage: {} server_IP server_port client_udp_port'.format(sys.argv[0]))
    exit()

server_IP = sys.argv[1]                 # IP of machine running server
server_port = int(sys.argv[2])          # Port number used by server
client_udp_port = int(sys.argv[3])      # Port client will listen for UDP traffic/beacons from other clients

# Setup TCP socket to communicate with server
client_tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_tcp_socket.settimeout(MAX_DELAY)
client_tcp_socket.connect((server_IP, server_port))

# Setup UDP socket for P2P Beaconing
client_udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

logged_in = False

while not logged_in:
    username = input('> Username: ')
    password = input('> Password: ')
    credentials = {
        'username': username,
        'password': password
    }
    client_tcp_socket.send(DataManager.encode_object(credentials))
    print('Sent packet')

    login_response = client_tcp_socket.recv(1024).decode('utf-8')
    login_response = int(login_response.replace('"', ''))

    if login_response == LoginStatus.SUCCESS:
        logged_in = True
        print('> Welcome to the BlueTrace Simulator.')
    elif login_response == LoginStatus.NOMATCH:
        print('> No account connected to the given username.')
    elif login_response == LoginStatus.WRONGPASSWORD:
        print('> Invalid Password. Please try again.')
    elif login_response == LoginStatus.BLOCKED:
        print('> Your account has been blocked due to multiple attempts. Please try again.')

client_tcp_socket.close()
client_udp_socket.close()


