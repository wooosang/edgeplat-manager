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

    def deploy(self,node):
        logging.debug("Ready to deploy [{}].".format(node.getName()))
        self.req = self.context.socket(zmq.REQ)
        self.req.connect("tcp://"+self.ip+":"+str(self.port))
        self.req.send_string(json.dumps(node.getJson()))
        result = self.req.recv_string()
        logging.debug("Deploy [{}] result: {}".format(node.getName(), result))