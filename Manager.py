# coding=UTF-8
import traceback,socket,yaml,logging,time,json, threading, queue, os
from nodes.NodeFactory import NodeFactory
from ManagerExt import ManagerExt
from configparser import ConfigParser

connect_timeout=30.0
socket.setdefaulttimeout(connect_timeout)
# recv_timeout=9.0

t_result = queue.Queue()

def _configAndSubscribe(node, parameter, debug):
    global t_result
    logging.debug("Debug mode: {}".format(debug))
    logging.debug("{} Start config node: [{}] \n".format(threading.current_thread().name, node.getName()))
    nodeip = node.getIp()
    nodeport = int(node.getPort())
    logging.debug("Begin connect to node [{}] {}:{}".format(node.getName(), nodeip, nodeport))
    sock = None
    if not debug and not node.debug:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(connect_timeout)
        sock.connect((nodeip, nodeport))
    config_command = node.getConfigCommand(parameter)
    # config_command = config_command | config
    logging.info("Config [%s] request: %s", node.getName(), config_command)
    if not debug and not node.debug:
        sock.sendall(json.dumps(config_command).encode())
        try:
            if hasattr(node, 'ignore_response') and node.ignore_response:
                time.sleep(0.1)
                result = 0
            else:
                result = sock.recv(1)
                result = int.from_bytes(result, 'big')
                if int(result)>0:
                    logging.error("Config node [{}] error,ready to receive {} bytes".format(node.getName(), int(result)))
                    msg = sock.recv(int(result))
                    logging.debug("{}".format(msg))
                    t_result.put(
                        (3, '>>> 配置节点 [{}] failed! Reason: {}'.format(node.getName(),msg.decode('utf-8'))))
                    return
            logging.debug("Config [{}] result: {}".format(node.getName(), result))
            msg = ''
            if result != 0:
                msg = 'Config node [{}] failed!'.format(node.getName())
            t_result.put((result, msg))
        except socket.timeout:
            t_result.put((3, '>>> Config node [{}] failed! Reason: Fetch result timeout！'.format(node.getName())))
            return
        except Exception as e:
            logging.error("Error!!! {}", e)

    subscribe_commands = node.getSubscribeCommand()
    if subscribe_commands:
        logging.info("Subscribe [%s] request: %s", node.getName(), subscribe_commands)
        if not debug and not node.debug:
            for subscribe_command in subscribe_commands:
                # logging.info("%s: %s", node.getName(), subscribe_command)
                sock.sendall(json.dumps(subscribe_command).encode())
                if hasattr(node, 'ignore_response') and node.ignore_response:
                    time.sleep(0.1)
                    result = 0
                else:
                    try:
                        result = sock.recv(1)
                        result = int.from_bytes(result, 'big')
                        logging.debug("Subscribe [{}] result: {}".format(node.getName(), result))
                    except Exception as e:
                        t_result.put((-1, ">>> Subscribe [{}] failed! Reason: {}".format(node.getName(), e)))
                        return
            sock.close()
            msg = ''
            if result != 0:
                msg = 'Subscribe node [{}] failed!'.format(node.getName())
            t_result.put((result, msg))

def _start(node, parameter, debug):
    sock = None
    global t_result
    try:
        nodeip = node.getIp()
        nodeport = int(node.getPort())
        start_command = node.getStartCommand(parameter)
        logging.info("Start [%s]: %s", node.getName(), start_command)
        if not debug and not node.debug:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(connect_timeout)
            sock.connect((nodeip, nodeport))
            sock.sendall(json.dumps(start_command).encode())
            if hasattr(node, 'ignore_response') and node.ignore_response:
                time.sleep(0.1)
                result = 0
            else:
                result = sock.recv(1)
                result = int.from_bytes(result, 'big')
                logging.debug("Start {} result: {}".format(node.getName(), result))
            if result != 0:
                t_result.put((-1, "Start [{}] failed! Start command return: {}".format(node.getName(), result)))

        logging.debug("Node [{}] started.".format(node.getName()))
    except Exception as e:
        logging.error("Start node [{}] failed！ Address:  {}:{}!!! Reason: {}".format(node.getName(), nodeip, nodeport, e))
        traceback.print_exc()
        t_result.put((-1, ">>> 启动节点 [{}] 失败！ 地址:  {}:{}!!! 原因: {}".format(node.getName(), nodeip, nodeport, e)))
    finally:
        if not debug and not node.debug and sock:
            sock.close()

#Stop异步执行方式暂未启用
def _stop(node, parameter, debug=False):
    sock = None
    nodeip = node.getIp()
    nodeport = int(node.getPort())
    logging.debug("Begin connect to node {} {}:{}".format(node.getName(), nodeip, nodeport))
    try:
        if not debug and not node.debug:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(connect_timeout)
            sock.connect((nodeip, nodeport))
        stop_command = node.getStopCommand()
        logging.debug("Send to [{}] command: {}".format(node.getName(), stop_command))
        if not debug and not node.debug:
            sock.send(json.dumps(stop_command).encode())
            if hasattr(node, 'ignore_response') and node.ignore_response:
                time.sleep(1)
                result = 0
            else:
                result = sock.recv(1)
                result = int.from_bytes(result, 'big')
            if result != 0:
                logging.error("停止节点[{}]失败！ Result: {}".format(node.getName(), result))
            else:
                logging.debug("Stop [{}] succeed! Result: {}".format(node.getName(), result))
    except Exception as e:
        logging.error(
            "Stop node [{}] failed！ Address:  {}:{}!!! Reason: {}".format(node.getName(), nodeip, nodeport, e))
        traceback.print_exc()
        t_result.put((-1, ">>> 停止节点 [{}] 失败！ 地址:  {}:{}!!! 原因: {}".format(node.getName(), nodeip, nodeport, e)))
    finally:
        if not debug and not node.debug and sock:
            sock.close()

    logging.debug("Node {} stopped.".format(node.getName()))

class Manager(object):
    def __init__(self,yml):
        configfile = 'manager.ini'
        conf = ConfigParser()  # 需要实例化一个ConfigParser对象
        conf.read(configfile)
        self.manager_config = conf
        logging.debug('Init config file {}'.format(yml))
        self.conf = yml
        self.edgenodes = {}
        with open(yml, 'r',encoding='utf-8') as file:
            edgeconfig = yaml.safe_load(file)
            self.name = edgeconfig['name']
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
                if isinstance(subscriber, str):
                    print('wrong '+subscriber)
                outbound = list(subscriber.keys())[0]
                outport = subscriber[outbound]
                if isinstance(outport,str) and '@' in outport:
                    self.edgenodes[edgenode].addOutboundWithCondition(self.edgenodes[outbound], outport.split('@')[0], outport.split('@')[1])
                else:
                    if outbound not in self.edgenodes:
                        raise Exception("{} not config correctly!".format(outbound))
                    self.edgenodes[edgenode].addOutbound(self.edgenodes[outbound], outport)
                self.edgenodes[outbound].addInbound(self.edgenodes[edgenode])

    def preStart(self, parameter):
        return ManagerExt.preStart(parameter)

    def postStart(self, parameter):
        return ManagerExt.postStart(parameter)

    def start(self, parameter, debug=False):#使用模版模式
        result = {"success": True}
        try:
            self.preStart(parameter)
            self.doStartAsync(parameter, debug)
            # self.doStart(parameter, debug)
            post_start_result = self.postStart(parameter)
            result.update(post_start_result)
        except Exception as e:
            result = {"success": False, "msg": str(e)}
        return result

    def doStartAsync(self, parameter, debug=False):
        start_time = time.time()
        config_thread_list = []
        start_thread_list = []
        for edgenode in self.edgenodes:
            node = self.edgenodes[edgenode]
            config_t = threading.Thread(target=_configAndSubscribe, args=( node, parameter, debug,))
            config_thread_list.append(config_t)
            start_t = threading.Thread(target=_start, args=(node, parameter, debug,))
            start_thread_list.append(start_t)
        for t in config_thread_list:
            t.setDaemon(True)
            t.start()
        for t in config_thread_list:
            t.join()
        logging.debug("All nodes config and subscribe done!")
        msg = ''
        success = True
        results = list()
        while not t_result.empty():
            results.append(t_result.get())
        for result in results:
            # logging.debug("{}".format(result))
            if int(result[0]) != 0:
                success = False
                logging.warn("{}".format(result))
                msg = msg + result[1] + "; "
        if not success:
            raise Exception("启动 {} 失败!    {}".format(self.name,msg))

        t_result.queue.clear()
        for t in start_thread_list:
            t.setDaemon(True)
            t.start()
        for t in start_thread_list:
            t.join()

        logging.debug('{} start nodes all done！'.format( threading.current_thread().name))
        logging.debug('Start all nodes total cost：{}s'.format( (time.time() - start_time)))

        results = list()
        while not t_result.empty():
            results.append(t_result.get())

        msg = ''
        success = True
        for result in results:
            logging.debug("{}".format(result))
            if int(result[0]) != 0:
                success = False
                msg = msg + result[1] + ';'
        if not success:
            raise Exception("启动节点失败!!!  {}".format(msg))
        return {}


    def doStart(self, parameter, debug=False):
        for edgenode in self.edgenodes:
            try:
                node = self.edgenodes[edgenode]
                nodeip = node.getIp()
                nodeport = int(node.getPort())
                logging.debug("Begin connect to node {} {}:{}".format(node.getName(), nodeip, nodeport))
                sock = None
                if not debug and not node.debug:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(connect_timeout)
                    sock.connect((nodeip, nodeport))
                config_command = node.getConfigCommand()
                # config_command = config_command | config
                logging.info("%s: %s",edgenode,config_command)
                if not debug and not node.debug:
                    sock.sendall(json.dumps(config_command).encode())
                    # sock.settimeout(recv_timeout)
                    if hasattr(node,'ignore_response') and node.ignore_response:
                        time.sleep(1)
                        result = 0
                    else:
                        result = sock.recv(4)
                        result = int.from_bytes(result, 'big')
                    logging.debug("Config {} result: {}".format(edgenode, result))
                    # sock.close()
                    if result != 0:
                        raise Exception("Config [{}] failed! Config command return: {}".format(edgenode, result))

                # if not debug and not node.debug:
                #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #     sock.settimeout(recv_timeout)
                #     sock.connect((nodeip, nodeport))
                subscribe_commands = self.edgenodes[edgenode].getSubscribeCommand()
                if subscribe_commands:
                    logging.info("Ready to send to %s: %s", edgenode, subscribe_commands)
                    if not debug and not node.debug:
                        for subscribe_command in subscribe_commands:
                            logging.info("%s: %s", edgenode, subscribe_command)
                            sock.sendall(json.dumps(subscribe_command).encode())
                            if hasattr(node, 'ignore_response') and node.ignore_response:
                                time.sleep(1)
                                result = 0
                            else:
                                result = sock.recv(1)
                                result = int.from_bytes(result, 'big')
                                logging.debug("Subscribe {} result: {}".format(edgenode, result))
                        # sock.close()
                        if result != 0:
                            raise Exception("Subscribe to [{}] failed! Subscribe command return: {}".format(edgenode, result))

                time.sleep(0.001)

                # if not debug and not node.debug:
                #     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #     sock.settimeout(recv_timeout)
                #     sock.connect((nodeip, nodeport))
                start_command = self.edgenodes[edgenode].getStartCommand(parameter)
                logging.info("%s: %s", edgenode,start_command)
                # sock.send(len(start_command))
                if not debug and not node.debug:
                    sock.sendall(json.dumps(start_command).encode())
                    if hasattr(node, 'ignore_response') and node.ignore_response:
                        time.sleep(1)
                        result = 0
                    else:
                        result = sock.recv(1)
                        result = int.from_bytes(result, 'big')
                        logging.debug("Start {} result: {}".format(edgenode, result))
                    # sock.close()
                    if result != 0:
                        raise Exception("Start [{}] failed! Start command return: {}".format(edgenode, result))
                logging.debug("Node {} started.".format(edgenode))
            except Exception as e:
                logging.error("Start node [{}] failed！ Address:  {}:{}!!! Reason: {}".format(edgenode, nodeip, nodeport, e))
                traceback.print_exc()
                raise Exception("Start node [{}] failed！ Address:  {}:{}!!! Reason: {}".format(edgenode, nodeip, nodeport, e))
            finally:
                if not debug and not node.debug:
                    sock.close()


    def preStop(self, debug=False):
        return ManagerExt.preStop(debug)

    def postStop(self, debug=False):
        return ManagerExt.postStop(debug)

    def stop(self, conf, debug=False):
        result = {'success': True}
        pre_stop_result = self.preStop(debug)
        result.update(pre_stop_result)
        # self.doStop(debug)
        self.doStopAsync(debug)
        self.postStop(debug)
        return result

    def doStopAsync(self, debug=False):
        start_time = time.time()
        stop_thread_list = []
        for edgenode in self.edgenodes:
            node = self.edgenodes[edgenode]
            stop_t = threading.Thread(target=_stop, args=(node, None, debug))
            stop_thread_list.append(stop_t)
        for t in stop_thread_list:
            t.setDaemon(True)
            t.start()
        for t in stop_thread_list:
            t.join()
        logging.debug("All nodes config and subscribe done!")


    def doStop(self, debug=False):
        nodeip = None
        nodeport = None
        for edgenode in self.edgenodes:
            try:
                node = self.edgenodes[edgenode]
                sock = None
                nodeip = node.getIp()
                nodeport = int(node.getPort())
                logging.debug("Begin connect to node [{}] {}:{}".format(node.getName(), nodeip, nodeport))
                if not debug and not node.debug:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(connect_timeout)
                    sock.connect((nodeip, nodeport))
                stop_command = self.edgenodes[edgenode].getStopCommand()
                logging.debug("Send to [{}] command: {}".format(edgenode, stop_command))
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
                logging.debug("Node [{}] stopped.".format(edgenode))
                # if not debug and not node.debug and sock:
                #     sock.close()
                #     logging.debug("Close connection to {}".format(edgenode))
            except Exception as e:
                msg = "Stop node [{}] failed!!! Address: {}:{} Reason: {}".format(edgenode, nodeip, nodeport, e)
                logging.error(msg)
                traceback.print_exc()
                raise Exception(msg)

            finally:
                if not debug and not node.debug:
                    sock.close()
                    logging.debug("Close connection to {}".format(edgenode))

    def deploy(self, agentHelpers, debug=False):
        for edgenode in self.edgenodes:
            try:
                node = self.edgenodes[edgenode]
                if str(node.getIp()) not in agentHelpers:
                    raise Exception("Agent on {} not exists!".format(node.getIp()))
                agentHelper = agentHelpers[node.getIp()]
                logging.debug("Begin deploy node [{}] by agent [{}]".format(node.getName(), agentHelper.getName()))
                agentHelper.deploy_node(node)
            except Exception as e:
                logging.error(e)
                raise e

    def deploy_monitor(self, agentHelpers):
        monitor_server_ip = self.manager_config['monitor']['server_ip']
        # logging.debug("Begin deploy monitor {} on server {}.".format(self.conf, monitor_server_ip))
        if str(monitor_server_ip) not in agentHelpers:
            raise Exception("Agent on {} not exists!".format(monitor_server_ip))

        monitor_server_helper = agentHelpers[str(monitor_server_ip)]


        #Deploy monitor slave
        slaves = {}
        for edgenode in self.edgenodes:
            node = self.edgenodes[edgenode]
            logging.debug("Add slave {}".format(node.getIp()))
            slaves[node.getIp()] = node.getIp()

        for slave in slaves:
            logging.debug("Deploy slave {}".format(slave))
            if slave not in agentHelpers:
                raise Exception("Agent on [{}] not exists!".format(slave))
            slaveAgentHelper = agentHelpers[slave]
            slaveAgentHelper.deploy_monitor_slave()
            monitor_server_helper.deploy_monitor_slave_config(slave)


        #Deploy node health check
        for edgenode in self.edgenodes:
            node = self.edgenodes[edgenode]
            logging.debug("Begin deploy monitor [{}]".format(node.getName()))
            logging.debug("Monitor conf: {}".format(node.getMonitor_conf()))
            monitor_server_helper.deploy_monitor_node_online_config(node)

