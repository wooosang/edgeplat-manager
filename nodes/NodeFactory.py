from nodes.CameraNode import CameraNode
from nodes.Node import Node
from nodes.UploaderNode import UploaderNode


class NodeFactory():
    @staticmethod
    def getNode(type, name, config):
        if type == '2DCamera':
            # print('构造2D相机采集节点.')
            edgenode = CameraNode(name, config)
            return edgenode
        if type == 'Uploader':
            # print('构造上传节点.')
            edgenode = UploaderNode(name, config)
            return edgenode
        return Node(name, config)