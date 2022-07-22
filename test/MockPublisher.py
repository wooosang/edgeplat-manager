import json, socket, threading

def handleCommand( clientSocket):
    # while True:
    data = clientSocket.recv(1024)
    print("Received: {}".format(data.decode('UTF-8')))
    # command = json.loads(data.decode('UTF-8'))
    result = 0
    clientSocket.send(result.to_bytes(1, 'big'))

if __name__ == '__main__':
    port = 8092
    socket = socket.socket()
    socket.bind(("", port))
    socket.listen()
    print("Listen on {} succeed!".format(port))
    while True:
        clientSocket,clientAddress = socket.accept()
        handleCommand(clientSocket)
        # handleCommandThread = threading.Thread(target=handleCommand, args=(clientSocket,))
        # handleCommandThread.start()