import json
import socket
import time

import pika
import requests as requests
from flask import Flask, jsonify, request
from Manager import Manager

app = Flask(__name__)
plc_url = 'http://192.168.10.10:1880/'
mq_host = '192.168.9.138'

credentials = pika.PlainCredentials('admin', 'softwork' )
connection = pika.BlockingConnection(pika.ConnectionParameters(mq_host, 5672, '/', credentials ,heartbeat=0))
channel = connection.channel()

@app.route("/start", methods=["POST"])
def start():
    global app
    param = request.json
    request_param = dict(param)
    # del request_param['packheight']
    # del request_param['checkcount']
    print(request_param)
    # packheight = param['packheight']
    # checkcount = param['checkcount']
    app.manager.stop()
    app.manager.startWithConfig(request_param)
    # response = startCheck(packheight, checkcount)
    return jsonify({'success':True})

@app.route('/stop', methods=['GET'])
def stop():
    global app
    response = requests.get(plc_url + 'deviceReset')
    app.manager.stop()
    return jsonify({'success':True})

def startPlc():
    response = requests.get(plc_url + 'deviceStart')
    time.sleep(1)
    response = requests.get(plc_url+'setMode?mode=1')
    response = requests.get(plc_url+'deviceInit')


def startCheck(packheight, checkcount):
    response = requests.get(plc_url + 'deviceReset')
    print("height={}, count={}".format(packheight,checkcount))
    response = requests.get(plc_url + 'setParams'+'?height='+str(packheight)+'&amount='+str(checkcount))
    response = requests.get(plc_url + 'testStart')
    return response


@app.route('/testStop', methods=['GET'])
def stopTest():
    global app
    global channel
    data = {'status': 'completed'}
    message = json.dumps(data)
    channel.basic_publish(exchange='test', routing_key='status', body=message)
    app.manager.stop()
    return jsonify({'success':True})

@app.route('/barcodeTest', methods=['GET'])
def rab():
    global channel
    data = {'barcode': 'WD000204543C1053'}
    message = json.dumps(data)
    channel.basic_publish(exchange='barcode', routing_key='barcode', body=message)
    return jsonify({'success': True})

@app.route('/deviceInit', methods=['GET'])
def deviceInit():
    response = requests.get(plc_url + 'deviceInit')
    return response

@app.route('/testsend', methods=['GET'])
def testsend():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 8080))
    sock.sendall({'command':'config'})
    sock.sendall({'command':'subscribe'})
    sock.close()


if __name__ == '__main__':
    app.manager = Manager('conf/edgeplat.yml')
    # startPlc()
    app.run(debug=True, host='0.0.0.0', port=9000)