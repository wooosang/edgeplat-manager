import threading
import time
from nodes.Node import Node

def configAndSubscribe(node):
    print("Start config node: {} \n".format(node.getName()))
    time.sleep(1)
    print('Node： ', threading.current_thread().name)
    time.sleep(1)


if __name__ == '__main__':

    start_time = time.time()

    print('Manager：', threading.current_thread().name)
    thread_list = []
    for i in range(5):
        t = threading.Thread(target=configAndSubscribe, args=(Node(str(i), {}), ))
        thread_list.append(t)

    for t in thread_list:
        t.setDaemon(True)
        t.start()

    for t in thread_list:
        t.join()

    print('Manager done！' , threading.current_thread().name)
    print('Total cost：', time.time()-start_time)
