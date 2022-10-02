import json, socket, threading

def handleCommand( clientSocket):
    # while True:
    data = clientSocket.recv(1024)
    print("Received: {}".format(data.decode('UTF-8')))
    # command = json.loads(data.decode('UTF-8'))
    result = 0
    clientSocket.send(result.to_bytes(1, 'big'))
        # if command['command'] == 'start':
        #     start(command)
        #     continue
        # if command['command'] == 'config':
        #     config(command)
        #     continue
        # if command['command'] == 'subscribe':
        #     subscribe(command)
        #     continue
        # if command['command'] == 'stop':
        #     stop(command)
        #     continue
    # clientSocket.close()

if __name__ == '__main__':
    port = 8081
    socket = socket.socket()
    socket.bind(("", port))
    socket.listen()
    print("Listen on {} succeed!".format(port))
    while True:
        clientSocket,clientAddress = socket.accept()
        handleCommand(clientSocket)
        # handleCommandThread = threading.Thread(target=handleCommand, args=(clientSocket,))
        # handleCommandThread.start()