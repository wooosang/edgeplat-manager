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
        logging.debug("Deploy monitor server [{}] result: {}".format(self.ip, result))
        return result

    def deploy_monitor_node(self):
        logging.debug("部署节点存活监控服务.......")
        #目前是使用promethues中的blackbox模块，故直接使用不再做其它处理

    def deploy_monitor_server_config(self):
        logging.debug("在prometheus上部署服务器资源监控配置......")
        #在配置文件夹中增加配置文件  server-ccd.json
        #[
        #   {
        #       "targets": [ "192.168.9.149:9100"]
        #   }
        #]

    def deploy_monitor_node_config(self, node):
        logging.debug("在prometheus上部署节点存活监控配置......")
        #在配置文件夹中增加配置文件node-ccd.json
        #[
        #   {
        #       "targets": [ "192.168.9.149:9011"],
        #       "labels": {
        #           "name": "voter",
	    #           "description": "投票节点"
        #       }
        #   }
        #]