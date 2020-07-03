import sys
import socket

if len(sys.argv) != 4:
    print('Usage: {} server_IP server_port client_udp_port'.format(sys.argv[0]))
    exit()

server_IP = sys.argv[1]                 # IP of machine running server
server_port = int(sys.argv[2])          # Port number used by server
client_udp_port = int(sys.argv[3])      # Port client will listen for UDP traffic/beacons from other clients


