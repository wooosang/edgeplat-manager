import traceback
import pika,signal,sys,zmq
from PyQt5.QtCore import QDataStream, QByteArray, QIODevice

testqueue='test'

print(zmq.__version__)

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.bind('tcp://*:5557')
socket.send_json({"command":"start"},flags=zmq.DONTWAIT)

def producer():
    context = zmq.Context(1)
    zmq_socket = context.socket(zmq.PUSH)
    # zmq_socket.setsockopt(zmq.SNDHWM, 10000)
    # zmq_socket.set_hwm(10000)
    # zmq_socket.setsockopt(zmq.LINGER, 0)
    # zmq_socket.setsockopt(zmq.SNDHWM, 10)
    # zmq_socket.setsockopt(zmq.SNDBUF, 10*1024)
    # zmq_socket.setsockopt(zmq.SNDTIMEO, 10)
    zmq_socket.bind("tcp://*:5555")
    # zmq_socket.setsockopt(zmq.LINGER, 0)

    # zmq_socket.set_hwm(10000)
    print('bind succeed.')
    zmq_socket.send_json({"command":"start"},flags=zmq.DONTWAIT)
    return zmq_socket

# sock = producer()

print('ready to receive message.')
def queue_callback(channel, method, properties, body):
  global socket
  try:
      if len(method.exchange):
        print("from exchange '{}': {}".format(method.exchange,body.decode('UTF-8')))
        sock.send_json(body.decode('UTF-8'),zmq.DONTWAIT)
      else:
        print("from queue {}: {}".format(method.routing_key,body.decode('UTF-8')))
        data = QByteArray()
        stream = QDataStream(data, QIODevice.WriteOnly)
        stream.writeQString(body.decode('UTF-8'))
        # stream.setVersion(QDataStream.Qt_4_6)
        sock.send(data)
        print('Forwar barcode succeed!')
  except Exception as e:
    print(e)
    traceback.print_exc()

def signal_handler(signal,frame):
  print("\nCTRL-C handler, cleaning up rabbitmq connection and quitting")
  connection.close()
  sys.exit(0)

credentials = pika.PlainCredentials('admin', 'softwork' )
connection = pika.BlockingConnection(pika.ConnectionParameters('192.168.9.138', 5672, '/', credentials ))
channel = connection.channel()

channel.basic_consume(queue=testqueue, on_message_callback=queue_callback, auto_ack=True)

# capture CTRL-C
signal.signal(signal.SIGINT, signal_handler)

print("Waiting for messages, CTRL-C to quit...")
print("")
channel.start_consuming()