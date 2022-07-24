from flask import Blueprint

ext_api = Blueprint('ext_api', __name__)

class ManagerExt():
    def __init__(self):
        pass

    @staticmethod
    def preStart(parameter, debug=False):
        return {}

    @staticmethod
    def postStart(parameter, debug=False):
        return {}

    @staticmethod
    def preStop(debug=False):
        return {}

    @staticmethod
    def postStop(debug=False):
        return {}