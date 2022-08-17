import traceback,socket,yaml,logging,time,json
from nodes.NodeFactory import NodeFactory
from ManagerExt import ManagerExt

connect_timeout=6.0
recv_timeout=9.0

class Manager(object):
    def __init__(self,yml):
        logging.debug('Init config file {}'.format(yml))
        self.edgenodes = {}
        with open(yml, 'r',encoding='utf-8') as file:
            edgeconfig = yaml.safe_load(file)
            nodes = edgeconfig["nodes"]
            for node_name in nodes:
                config = nodes[node_name]
                node_type = None
                if 'type' in config:
                    node_type = config['type']
                edgenode = NodeFactory.getNode(node_type, node_name, config)
                self.edgenodes[node_name] = edgenode

        for edgenode in self.edgenodes:
            subscribers = self.edgenodes[edgenode].getSubscribers()
            for subscriber in subscribers:
                outbound = list(subscriber.keys())[0]
                outport = subscriber[outbound]
                if isinstance(outport,str) and '@' in outport:
                    self.edgenodes[edgenode].addOutboundWithCondition(self.edgenodes[outbound], outport.split('@')[0], outport.split('@')[1])
                else:
                    self.edgenodes[edgenode].addOutbound(self.edgenodes[outbound], outport)
                self.edgenodes[outbound].addInbound(self.edgenodes[edgenode])

    def preStart(self, parameter):
        return ManagerExt.preStart(parameter)

    def postStart(self, parameter):
        return ManagerExt.postStart(parameter)

    def start(self, parameter, debug=False):
        result = {"success": True}
        try:
            self.preStart(parameter)
            self.stop(debug)
            self.doStart(parameter, debug)
            # response = startCheck(packheight, checkcount)
            post_start_result = self.postStart(parameter)
            # merged_result = {key: value for (key, value) in (result.items() + post_start_result.items())}
            result.update(post_start_result)
        except Exception as e:
            result = {"success": False, "msg": str(e)}
        return result

    def doStart(self, parameter, debug=False):
        for edgenode in self.edgenodes:
            try:
                node = self.edgenodes[edgenode]
                nodeip = node.getIp()
                nodeport = int(node.getPort())
                logging.debug("Begin connect to node {} {}:{}".format(node.getName(), nodeip, nodeport))
                if not debug and not node.debug:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(connect_timeout)
                    sock.connect((nodeip, nodeport))
                config_command = node.getConfigCommand()
                # config_command = config_command | config
                logging.info("%s: %s",edgenode,config_command)
                if not debug and not node.debug:
                    sock.send(json.dumps(config_command).encode())
                    sock.settimeout(recv_timeout)
                    if hasattr(node,'ignore_response') and node.ignore_response:
                        time.sleep(1)
                        result = 0
                    else:
                        result = sock.recv(4)
                        result = int.from_bytes(result, 'big')
                    logging.debug("Config {} result: {}".format(edgenode, result))
                    sock.close()
                    if result != 0:
                        raise Exception("配置{}失败! 配置命令返回: {}".format(edgenode, result))

                if not debug and not node.debug:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(recv_timeout)
                    sock.connect((nodeip, nodeport))
                subscribe_commands = self.edgenodes[edgenode].getSubscribeCommand()
                if subscribe_commands:
                    logging.info("%s: %s",edgenode,subscribe_commands)
                    if not debug and not node.debug:
                        for subscribe_command in subscribe_commands:
                            sock.send(json.dumps(subscribe_command).encode())
                            if hasattr(node, 'ignore_response') and node.ignore_response:
                                time.sleep(1)
                                result = 0
                            else:
                                result = sock.recv(1)
                                result = int.from_bytes(result, 'big')
                        sock.close()
                        if result != 0:
                            raise Exception("订阅到{}失败! 订阅命令返回 {}".format(edgenode, result))

                if not debug and not node.debug:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(recv_timeout)
                    sock.connect((nodeip, nodeport))
                start_command = self.edgenodes[edgenode].getStartCommand(parameter)
                logging.info("%s: %s", edgenode,start_command)
                # sock.send(len(start_command))
                if not debug and not node.debug:
                    sock.send(json.dumps(start_command).encode())
                    if hasattr(node, 'ignore_response') and node.ignore_response:
                        time.sleep(1)
                        result = 0
                    else:
                        result = sock.recv(1)
                        result = int.from_bytes(result, 'big')
                    sock.close()
                    if result != 0:
                        raise Exception("Start [{}] failed! Start command return {}".format(edgenode, result))
                logging.debug("Node {} started.".format(edgenode))
            except Exception as e:
                logging.error("Start node {} failed！ Address:  {}:{}!!! Reason: {}".format(edgenode, nodeip, nodeport, e))
                traceback.print_exc()
                raise Exception("Start node{} failed！ Address:  {}:{}!!! Reason: {}".format(edgenode, nodeip, nodeport, e))
            finally:
                if not debug and not node.debug:
                    sock.close()


    def preStop(self, debug=False):
        return ManagerExt.preStop(debug)

    def postStop(self, debug=False):
        return ManagerExt.postStop(debug)

    def stop(self, debug=False):
        result = {'success': True}
        pre_stop_result = self.preStop(debug)
        result.update(pre_stop_result)
        self.doStop(debug)
        self.postStop(debug)
        return result

    def doStop(self, debug=False):
        for edgenode in self.edgenodes:
            try:
                node = self.edgenodes[edgenode]
                sock = None
                nodeip = node.getIp()
                nodeport = int(node.getPort())
                logging.debug("Begin connect to node {} {}:{}".format(node.getName(), nodeip, nodeport))
                if not debug and not node.debug:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(connect_timeout)
                    sock.connect((nodeip, nodeport))
                stop_command = self.edgenodes[edgenode].getStopCommand()
                logging.debug("Send to {} command: {}".format(edgenode, stop_command))
                if not debug and not node.debug:
                    sock.send(json.dumps(stop_command).encode())
                    if hasattr(node, 'ignore_response') and node.ignore_response:
                        time.sleep(1)
                        result = 0
                    else:
                        result = sock.recv(1)
                        result = int.from_bytes(result, 'big')
                    if result != 0:
                        logging.error("停止节点[{}]失败！ Result: {}".format(edgenode, result))
                    else:
                        logging.debug("Stop {} succeed! Result: {}".format(edgenode,result))
                    # time.sleep(0.1)
                logging.debug("Node {} stopped.".format(edgenode))
                if not debug and not node.debug and sock:
                    sock.close()
                    logging.debug("Close connection to {}".format(edgenode))
            except Exception as e:
                msg = "Stop node [{}] failed!!! Reason: {}".format(edgenode, e)
                logging.error(msg)
                traceback.print_exc()
                raise Exception(msg)

            finally:
                if not debug and not node.debug:
                    sock.close()

