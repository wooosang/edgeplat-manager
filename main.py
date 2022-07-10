
import socket,pickle,json,zmq, time, yaml,logging
import traceback

from Node import Node

edgenodes = {}
debug=False

log_file_format = "[%(levelname)s] - %(asctime)s - %(name)s - : %(message)s in %(pathname)s:%(lineno)d"
log_console_format = "[%(levelname)s] - %(asctime)s - %(pathname)s:%(lineno)d : %(message)s"
main_logger = logging.getLogger()
main_logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(log_console_format))
main_logger.addHandler(console_handler)

with open('conf/test.yml', 'r') as file:
    edgeconfig = yaml.safe_load(file)
    nodes = edgeconfig["nodes"]
    for node in nodes:
        edgenode = Node(node,nodes[node])
        edgenodes[node] = edgenode

for edgenode in edgenodes:
    subscribers = edgenodes[edgenode].getSubscribers()
    for subscriber in subscribers:
        # subconf = subscriber.split(':')
        outbound = list(subscriber.keys())[0]
        outport = subscriber[outbound]
        # outbound = subconf[0]
        # outport = subconf[1]
        edgenodes[edgenode].addOutbound(edgenodes[outbound], outport)
        edgenodes[outbound].addInbound(edgenodes[edgenode])

# Create a socket (SOCK_STREAM means a TCP socket)
try:
    # Connect to server and send data

    for edgenode in edgenodes:
        try:
            node = edgenodes[edgenode]
            nodeip = node.getIp()
            nodeport = int(node.getPort())
            print("Begin connect to node {} {}:{}".format(node.getName(), nodeip, nodeport))
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((nodeip, nodeport))
            config_command = node.getConfigCommand()
            logging.debug(config_command)
            if not debug:
                sock.sendall(json.dumps(config_command).encode())
                time.sleep(1)
            subscribe_command = edgenodes[edgenode].getSubscribeCommand()
            print(subscribe_command)
            if not debug:
                sock.send(json.dumps(subscribe_command).encode())
                time.sleep(1)
            start_command = edgenodes[edgenode].getStartCommand()
            print(start_command)
            if not debug:
                sock.send(json.dumps(start_command).encode())
                time.sleep(1)
            print("Node {} started.".format(edgenode))
        except Exception as e:
            print("Can't connect to node {}!!! {}".format(edgenode,e))
            traceback.print_exc()
    # sock.send(data.encode())
    # sock.sendall(bytes(data,encoding="utf-8"))


    # Receive data from the server and shut down
    # received = sock.recv(1024)
    # received = received.decode("utf-8")

finally:
    sock.close()

# print("Received: {}".format(received))
