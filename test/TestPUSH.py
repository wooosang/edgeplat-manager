import time

import zmq

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.bind('tcp://*:5557')
while True:
    socket.send_string('ok',zmq.DONTWAIT)
    print('ok.............')
    time.sleep(1)