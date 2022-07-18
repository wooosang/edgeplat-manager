import traceback,socket,yaml,logging,time,json
from Node import Node

debug=False

class Manager(object):
    def __init__(self,yml):
        print('Init config file {}'.format(yml))
        self.edgenodes = {}
        with open(yml, 'r') as file:
            edgeconfig = yaml.safe_load(file)
            nodes = edgeconfig["nodes"]
            for node in nodes:
                edgenode = Node(node, nodes[node])
                self.edgenodes[node] = edgenode

        for edgenode in self.edgenodes:
            subscribers = self.edgenodes[edgenode].getSubscribers()
            for subscriber in subscribers:
                outbound = list(subscriber.keys())[0]
                outport = subscriber[outbound]
                self.edgenodes[edgenode].addOutbound(self.edgenodes[outbound], outport)
                self.edgenodes[outbound].addInbound(self.edgenodes[edgenode])

    def startWithConfig(self,config):
        for edgenode in self.edgenodes:
            try:
                node = self.edgenodes[edgenode]
                nodeip = node.getIp()
                nodeport = int(node.getPort())
                print("Begin connect to node {} {}:{}".format(node.getName(), nodeip, nodeport))
                if not debug:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((nodeip, nodeport))
                config_command = node.getConfigCommand()
                # config_command = config_command | config
                logging.debug(config_command)
                print(config_command)
                if not debug:
                    sock.sendall(json.dumps(config_command).encode())
                    result = sock.recv(1)
                    sock.close()

                if not debug:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((nodeip, nodeport))
                subscribe_command = self.edgenodes[edgenode].getSubscribeCommand()
                print(subscribe_command)
                # sock.send(len(subscribe_command))
                if not debug:
                    sock.sendall(json.dumps(subscribe_command).encode())
                    result = sock.recv(1)
                    sock.close()

                if not debug:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((nodeip, nodeport))
                start_command = self.edgenodes[edgenode].getStartCommand()
                for key in config:
                    start_command[key] = config[key]
                # start_command['checkbatchpk'] = config['checkbatchpk']
                print(start_command)
                # sock.send(len(start_command))
                if not debug:
                    sock.sendall(json.dumps(start_command).encode())
                    result = sock.recv(1)
                    sock.close()
                print("Node {} started.".format(edgenode))
            except Exception as e:
                print("Can't connect to node {}!!! {}".format(edgenode, e))
                traceback.print_exc()
            finally:
                if not debug:
                    sock.close()

    def start(self):
        for edgenode in self.edgenodes:
            try:
                node = self.edgenodes[edgenode]
                nodeip = node.getIp()
                nodeport = int(node.getPort())
                print("Begin connect to node {} {}:{}".format(node.getName(), nodeip, nodeport))
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((nodeip, nodeport))
                config_command = node.getConfigCommand()
                logging.debug(config_command)
                sock.sendall(json.dumps(config_command).encode())
                time.sleep(0.1)
                subscribe_command = self.edgenodes[edgenode].getSubscribeCommand()
                print(subscribe_command)
                sock.send(json.dumps(subscribe_command).encode())
                time.sleep(0.1)
                start_command = self.edgenodes[edgenode].getStartCommand()
                print(start_command)
                sock.send(json.dumps(start_command).encode())
                time.sleep(0.1)
                print("Node {} started.".format(edgenode))
            except Exception as e:
                print("Can't connect to node {}!!! {}".format(edgenode, e))
                traceback.print_exc()
            finally:
                sock.close()

    def stop(self):
        for edgenode in self.edgenodes:
            try:
                node = self.edgenodes[edgenode]
                nodeip = node.getIp()
                nodeport = int(node.getPort())
                print("Begin connect to node {} {}:{}".format(node.getName(), nodeip, nodeport))
                if not debug:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((nodeip, nodeport))
                stop_command = self.edgenodes[edgenode].getStopCommand()
                print(stop_command)
                if not debug:
                    sock.send(json.dumps(stop_command).encode())
                    time.sleep(0.1)
                print("Node {} stopped.".format(edgenode))
            except Exception as e:
                print("Can't connect to node {}!!! {}".format(edgenode, e))
                traceback.print_exc()
            finally:
                if not debug:
                    sock.close()