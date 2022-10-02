import time, io, zmq
from PyQt5 import QtCore

context = zmq.Context(1)
sub = context.socket(zmq.SUB)
endpoint="tcp://192.168.9.138:5558"
sub.setsockopt(zmq.SUBSCRIBE, "".encode("utf-8"))
sub.connect(endpoint)
while True:
    data = sub.recv()
    print("Received some data...........")
    print(data)
    print(len(data))
    # if(len(data)>1):
    #     with open("test.jpg", "wb") as binary_file:
    #         # Write bytes to file
    #         binary_file.write(data)
    #         break
    # buf = QtCore.QByteArray.fromRawData(data)
    # ds = QtCore.QDataStream(buf)
    # context = ds.readQString()
    # print(context)
    # len_data = ds.readRawData(4)
    # int_len_data = int.from_bytes(len_data, "big")
    # print(int_len_data)
    #data = ds.readRawData(int_len_data)
    # with open("image.png", "wb") as f:
    #     f.write(data)
    # time.sleep(1)