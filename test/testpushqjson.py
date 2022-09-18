import zmq, random, json, time
from PyQt5.QtCore import QDataStream, QByteArray, QIODevice

def send(sock):
    data = QByteArray()
    stream = QDataStream(data, QIODevice.WriteOnly)
    body = dict()
    body['idx'] = random.randint(1,10)
    imagefile = "wyccd/defect.jpg"
    body['filename'] = imagefile
    print('Send {}'.format(body))
    stream.writeQString(json.dumps(body))


    try:
        sock.send(data, zmq.DONTWAIT)
        print('Send image succeed!')
    except:
        pass

if __name__ == '__main__':
    IP = '192.168.9.138'
    PORT= 5555
    FACE = 'A'
    context = zmq.Context(2)
    push_socket = context.socket(zmq.PUSH)
    push_socket.set_hwm(5)
    push_socket.bind("tcp://*:{}".format(PORT))
    while True:
        send(push_socket)
        time.sleep(1)