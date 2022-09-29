import pika,time,json
import requests as requests
from flask import Blueprint

ext_api = Blueprint('ext_api', __name__)
credentials = pika.PlainCredentials('admin', 'softwork')
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.10.10', 5672, '/', credentials))
channel = connection.channel()
plc_url = 'http://192.168.10.10:1880/'


@ext_api.route('/testStop', methods=['GET'])
def stopTest():
    global appExt
    print('PLC结束，MQ发送通知.')
    result = ext_api.manager.stop()
    global channel
    data = {'status': 'stop'}
    message = json.dumps(data)
    channel.basic_publish(exchange='test', routing_key='status', body=message)
    return result

class ManagerExt():

    @staticmethod
    def startPlc():
        response = requests.get(plc_url + 'deviceStart')
        time.sleep(2)
        response = requests.get(plc_url + 'deviceInit')
        return response

    @staticmethod
    def preStart(parameter, debug=False):
        return ManagerExt.startPlc()

    @staticmethod
    def startCheck(diameter):
        print("Diameter={}".format(diameter))
        response = requests.get(plc_url + 'setMode?mode=1')
        response = requests.get(plc_url + 'setParams' + '?d=' + str(diameter))
        response = requests.get(plc_url + 'testStart')
        return response

    @staticmethod
    def postStart(parameter, debug=False):
        diameter = parameter['diameter']
        response = ManagerExt.startCheck(diameter)
        return response



    @staticmethod
    def preStop(debug=False):
        return {'msg':'plc停止成功!'}

    @staticmethod
    def postStop(debug=False):
        pass
