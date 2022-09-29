import zmq
context=zmq.Context()
socket=context.socket(zmq.PUSH)   #设置socket类型PUSH推送
socket.bind("tcp://*:5555")       #绑定IP和端口

while True:
    data=input("input your data:")
    socket.send_string(data)