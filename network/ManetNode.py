'''
MANET网络的构建：
1、节点网络
    1.1 共享密钥
    1.2 加密解密
    1.3 通信半径
'''
import copy
from enum import Enum
from matplotlib.pyplot import plot, show

COST = 1 / (2 ** 7)  # 节点转发消息时的成本

# 定义子网络类型
class Type(Enum):
    external = 0
    subnet_1 = 1
    subnet_2 = 2
    subnet_3 = 3
    subnet_4 = 4
    subnet_5 = 5
    subnet_6 = 6
    subnet_7 = 7
    subnet_8 = 8


class ManetNode(object):
    def __init__(self, mac, type):
        global COST
        self.mac = mac  #节点的id
        self.type = type  # 节点种节点身份类（属于哪家公司）
        self.route_table = dict()
        self.position = list() #节点的坐标
        self.color_value = (0,0,1) #节点的颜色

        self.neighbor = list()  # 节点维护的邻居列表
        self.send_message_pool = list()  # 节点自己需要发送的消息池
        self.buffer_message_pool = list()  # 节点的缓存池，暂时保存从别的节点那里接收到的消息
        self.transport_message_pool = list()  # 从缓存池中拿出来的需要立即转发的消息
        self.receive_message_pool = list()  # 用来接收发送给自己的消息

        self.qs_buffer_message_pool = set()  # 用来快速进行查找
        self.qs_send_message_pool = set()
        self.qs_receive_message_pool = set()
        self.qs_transport_message_pool = set()


    def __str__(self):
        return '%s' % self.mac

    __repr__ = __str__

    def clear(self):
        self.send_message_pool = list()  # 节点自己需要发送的消息池
        self.buffer_message_pool = list()  # 节点的缓存池，暂时保存从别的节点那里接收到的消息
        self.transport_message_pool = list()  # 从缓存池中拿出来的需要立即转发的消息
        self.receive_message_pool = list()  # 用来接收发送给自己的消息

        self.qs_buffer_message_pool = set()  # 用来快速进行查找
        self.qs_send_message_pool = set()
        self.qs_receive_message_pool = set()
        self.qs_transport_message_pool = set()



    # 节点转发消息（Broker）
    def transport_message(self):
        """
        1：如果发送池中有消息的话优先发送发送池中的数据
        2：如果暂存池中有消息待转发，则选择根据价格策略选择一个价格较高的数据包
        3：对选择的数据包进行处理：从暂存池中移除,将数据包添加进转发池中，返回数据包
        """
        # if len(self.send_message_pool) > 0:
        #     # 需要从发送池中取出一个消息
        #     send_message = self.send_message_pool[0]
        #     self.send_message_pool.remove(send_message)
        #     # if send_message.flag == True:
        #     self.qs_transport_message_pool.add(send_message.id)
        #     return send_message
        if len(self.buffer_message_pool) > 0:
            buffer_message = self.buffer_message_pool[0]  # 取出缓存池中的第一个数据包
            # self.qs_transport_message_pool.add(buffer_message.id)
            self.buffer_message_pool.remove(buffer_message)  # 将该数据包从缓存池中删除,注意这里的qs_buffer_message_pool并没有删除
            return buffer_message
        else:
            return None

    # 节点接收消息 (Receiver)
    def receive_message_old(self, package):
        if package.head[0] == self.mac:
            return False  # 节点收到自己发出的消息
        elif package.head[1] == self.mac:
            if package.id in self.qs_receive_message_pool:  # 之前收到过该数据包
                return False  # node已经接收过该消息
            else:  # 第一次收到该数据包
                self.receive_message_pool.append(package)
                self.qs_receive_message_pool.add(package.id)  # 更新接收消息池
                return True
        else:  # 表明该数据包不是发送给自己的
            if package.id in self.qs_buffer_message_pool:
                return False  # node已经暂存过该消息
            else:
                self.buffer_message_pool.append(package)
                self.qs_buffer_message_pool.add(package.id)  # node成功暂存了消息
                return True

    def receive_message(self, package):
        self.buffer_message_pool.append(package)
        # self.qs_buffer_message_pool.add(package.id)  # node成功暂存了消息
        return True


if __name__ == '__main__':
    n1 = ManetNode(1, 'A')
    n2 = ManetNode(2, 'B')
    # slot = 0
    # plot(n1.pos_Matrix[0], n1.pos_Matrix[1])
    # show()
    # n2.mobile(2)
    # print(n2.pos)
