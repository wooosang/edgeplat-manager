from nodes.CameraNode import CameraNode
from nodes.Node import Node

class NodeFactory():
    @staticmethod
    def getNode(type, name, config):
        if type == '2DCamera':
            print('构造2D相机采集节点.')
            edgenode = CameraNode(name, config)
            return edgenode
        return Node(name, config)