import logging, zmq, json

class AgentHelper(object):
    def __init__(self):
        self.context = zmq.Context()

    def parseConfig(self, config):
        self.ip = config['agent_ip']
        self.port = config['agent_port']
        self.code = config['agent_code']
        self.name = config['agent_name']

    def getCode(self):
        return self.code

    def getName(self):
        return self.name

    def deploy_node(self,node):
        logging.debug("Ready to deploy [{}].".format(node.getName()))
        self.req = self.context.socket(zmq.REQ)
        self.req.connect("tcp://"+self.ip+":"+str(self.port))
        command={}
        command['command'] = 'deploy_node'
        command['config'] = node.getJson()
        self.req.send_string(json.dumps(command))
        result = self.req.recv_string()
        logging.debug("Deploy [{}] result: {}".format(node.getName(), result))

    def deploy_monitor_slave(self):
        logging.debug("部署节点服务器资源监控服务......")
        #目前是部署node_exporter容器
        self.req = self.context.socket(zmq.REQ)
        self.req.connect("tcp://" + self.ip + ":" + str(self.port))
        command = {}
        command['command'] = 'deploy_monitor_slave'
        command['config'] = {}
        self.req.send_string(json.dumps(command))
        result = self.req.recv_string()
        logging.debug("Deploy monitor slave on [{}] result: {}".format(self.ip, result))
        return result

    def deploy_monitor_node(self):
        logging.debug("部署节点存活监控服务.......")
        self.req = self.context.socket(zmq.REQ)
        self.req.connect("tcp://" + self.ip + ":" + str(self.port))
        command = {}
        command['command'] = 'deploy_monitor_node'
        command['config'] = {}
        self.req.send_string(json.dumps(command))
        result = self.req.recv_string()
        self.req.close()
        logging.debug("Deploy monitor node [{}] result: {}".format(self.ip, result))
        return result

    def deploy_monitor_slave_config(self, slave_ip):
        logging.debug("在prometheus上部署服务器[{}]资源监控配置......".format(slave_ip))
        self.req = self.context.socket(zmq.REQ)
        self.req.connect("tcp://" + self.ip + ":" + str(self.port))
        command = {}
        command['command'] = 'deploy_monitor_slave_config'
        command['config'] = {"ip":slave_ip}
        self.req.send_string(json.dumps(command))
        result = self.req.recv_string()
        logging.debug("Deploy monitor slave [{}] config result: {}".format(self.ip, result))
        return result

    def deploy_monitor_node_online_config(self, node):
        logging.debug("在prometheus上部署节点存活监控配置......")
        self.req = self.context.socket(zmq.REQ)
        self.req.connect("tcp://" + self.ip + ":" + str(self.port))
        command = {}
        command['command'] = 'deploy_monitor_node_online_config'
        command['config'] = {"blackbox_config": node.getMonitor_conf(),"node_name": node.getName()}
        self.req.send_string(json.dumps(command))
        result = self.req.recv_string()
        logging.debug("Deploy monitor slave [{}] config result: {}".format(self.ip, result))
        return result