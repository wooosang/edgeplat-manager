class Node:
    def __init__(self, name,config):
        self.name = name
        self.subscribers = {}
        self.subscribersCondition = {}
        self.sources = []
        self.yml = config
        self.debug = False
        if 'type' in config:
            self.type = config['type']
        if 'code' in config:
            self.code = config['code']
        if 'ignore_response' in config:
            self.ignore_response = config['ignore_response']
        if 'debug' in config:
            self.debug = config['debug']
        endpoint = config['endpoint'].split(':')
        self.ip = endpoint[0]
        self.port = endpoint[1]
        if 'config' in config:
            self.config = config["config"]
            if self.config is None:
                self.config = {}
        else:
            self.config = {}

    def getName(self):
        return self.name

    def getIp(self):
        return self.ip

    def getPort(self):
        return self.port

    def getSubscribers(self):
        if 'subscriber' in self.yml:
            return self.yml['subscriber']
        return []

    def addOutbound(self,sink,port):
        self.subscribers[sink.getName()] = port

    def addOutboundWithCondition(self, sink, port, condition):
        self.subscribers[sink.getName()] = port
        self.subscribersCondition[sink.getName()] = condition

    def addInbound(self,source):
        self.sources.append(source)

    def getOutboundPort(self, node):
        return self.subscribers[node]

    def getConfigCommand(self, parameter={}):
        if 'wrapped' in self.config and self.config['wrapped']:
            config_command = {}
            config_command['config'] = self.config
        else:
            config_command = self.config
        config_command['command'] = 'config'

        if self.hasConfig('cameraip') and self.sources:
            config_command['pull_endpoint'] = 'tcp://' + self.sources[0].getIp() + ':' + str(self.sources[0].getOutboundPort(self.getName()))

        return config_command

    def getSubscribeCommand(self):
        if len(self.subscribers) == 0:
            return None
        commands = []

        for sink in self.subscribers:
            subscribe_command = {'command': 'subscribe'}
            subscribe_command['endpoint'] = 'tcp://*:'+str(self.getOutboundPort(sink))
            subscribe_command['port'] = self.getOutboundPort(sink)
            if sink in self.subscribersCondition:
                subscribe_command['condition'] = self.subscribersCondition[sink]
            commands.append(subscribe_command)
        return commands

    def getStartCommand(self, parameter={}):
        start_command = {}
        if len(self.sources)>1:
            sources=[];
            for source in self.sources:
                consume = 'tcp://'+source.getIp()+':'+str(source.getOutboundPort(self.getName()))
                # print(consume)
                sources.append(consume)
                start_command['endpoints'] = sources
        elif len(self.sources)==1:
            consume = 'tcp://' + self.sources[0].getIp() + ':' + str(self.sources[0].getOutboundPort(self.getName()))
            start_command['endpoint'] = consume

        start_command['command'] = 'start'
        return start_command

    def getStopCommand(self):
        stop_command = {}
        stop_command['command']='stop'
        return stop_command

    def getConfig(self, key):
        return self.config[key]

    def hasConfig(self, key):
        return key in self.config