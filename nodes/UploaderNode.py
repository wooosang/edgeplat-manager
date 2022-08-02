from nodes.Node import Node

class UploaderNode(Node):
    def __init__(self, name, config):
        super(UploaderNode, self).__init__(name, config)

    def getStartCommand(self, parameter={}):
        startCommand = super(UploaderNode, self).getStartCommand(parameter)
        if 'endpoint' in startCommand:
            del startCommand['endpoint']
        sources = [];
        for source in self.sources:
            consume = 'tcp://' + source.getIp() + ':' + str(source.getOutboundPort(self.getName()))
            # print(consume)
            sources.append(consume)
            startCommand['endpoints'] = sources
        return startCommand