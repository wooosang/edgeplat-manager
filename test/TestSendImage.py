import json, sys, time, zmq
import logging

from PyQt5.QtCore import QDataStream, QByteArray, QIODevice

index=0

def send(sock,IP,FACE):

    global index
    data = QByteArray()
    stream = QDataStream(data, QIODevice.WriteOnly)
    body = dict()
    body['cameraip']=IP
    index = index + 1
    body['idx']=index
    body['face'] = FACE
    imagefile = "wyccd/defect.jpg"
    body['filename'] = imagefile
    # print('send image.....' + imagefile)
    print('Send {}'.format(body))
    stream.writeQString(json.dumps(body))

    with open(imagefile, "rb") as img_file:
        bytes = img_file.read()
        stream.writeBytes(bytes)

    try:
        sock.send(data, zmq.DONTWAIT)
        print('Send image succeed!')
    except:
        pass


if __name__ == '__main__':
    IP = '192.168.9.138'
    PORT= 6688
    FACE = 'A'
    context = zmq.Context(2)
    push_socket = context.socket(zmq.PUSH)
    push_socket.set_hwm(5)
    push_socket.bind("tcp://*:{}".format(PORT))
    while True:
        send(push_socket, IP, FACE)
        time.sleep(1)