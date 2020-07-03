import sys
import socket

if len(sys.argv) != 3:
    print('Usage: {} server_port block_duration'.format(sys.argv[0]))
    exit()

print(sys.argv)
server_port = int(sys.argv[1])
block_duration = int(sys.argv[2])   # Duration (seconds) user will be blocked after 3 unsuccessful login attempts
