from nodes.Node import Node
import logging

class CameraNode(Node):
    def __init__(self, name, config):
        super(CameraNode,self).__init__(name,config)

    def getConfigCommand(self, parameter={}):
        configCommand = super(CameraNode, self).getConfigCommand(self)
        return configCommand

    def getSubscribeCommand(self):
        subscribeCommands = super(CameraNode, self).getSubscribeCommand()
        if subscribeCommands:
            for subscribeCommand in subscribeCommands:
                subscribeCommand['cameraip'] = self.config['cameraip']
        return subscribeCommands

    def getStartCommand(self, parameter={}):
        startCommand = super(CameraNode, self).getStartCommand(parameter)
        startCommand['cameraip'] = self.config['cameraip']
        if parameter and 'node_parameter' in parameter:
            node_parameter = parameter["node_parameter"]
        else:
            node_parameter = {}
        for key in parameter:
            if key != 'node_parameter':
                startCommand[key] = parameter[key]

        if self.code in node_parameter:
            dynamic_parameter = node_parameter[self.code]
            # print("获取到动态参数: {}".format(dynamic_parameter))
            for key in dynamic_parameter:
                startCommand[key] = dynamic_parameter[key]
        return startCommand