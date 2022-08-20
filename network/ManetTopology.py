'''
考虑构建一张图：MANET网络拓扑
使用networkx
根据输入的节点与边的信息，构建网络拓扑：
1、刚开始可以给定固定的拓扑
2、之后会考虑一定时间内刷新网络拓扑
'''
import copy

import community

from network.ManetNode import ManetNode, Type
import re
import networkx as nx

from network.Event_monitoring import Event_monitor


class Subnet(object):
    def __init__(self, type):
        self.type = type
        self.node_list = list()
        self.incoming_event_monitor = list()
        self.outcoming_event_monitor = list()
        self.internal_event_monitor = list()

    def __str__(self):
        return 'Network_Type:%s' % self.type + 'Node_list:%s' % self.node_list

    def clear_event(self):
        for e in self.incoming_event_monitor:
            e.clear_e()
        for e in self.internal_event_monitor:
            e.clear_e()
        for e in self.outcoming_event_monitor:
            e.clear_e()

    __repr__ = __str__


def manet_generator():  # 不考虑节点的移动性，固定拓扑
    Edge_data = list()
    G_temp = nx.Graph()
    G = nx.Graph()
    node = []
    with open('../拓扑文件/as19990829.txt', 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line.strip('\n')  # 去掉列表中每一个元素的换行符
            temp_list = re.split(r'\s+', line)
            if temp_list[0] == '#':
                continue
            temp_edge = (int(temp_list[0]), int(temp_list[1]))
            G_temp.add_nodes_from(temp_edge)
            Edge_data.append(temp_edge)
    for N in G_temp.nodes():
        node.append(ManetNode(mac=N, type='A'))
    for edge in Edge_data:
        for i in node:
            if i.mac == edge[0]:
                for j in node:
                    if j.mac == edge[1]:
                        G.add_edge(i, j)
    # print("输出图的信息：", G.edges)
    # 初始化节点的邻居列表
    for temp1 in G.nodes():  # 根据图的全局性获得每个节点的邻居信息
        temp1_neighbor = nx.neighbors(G, temp1)
        while True:
            try:  # 迭代获得邻居节点信息
                x = next(temp1_neighbor)
                if x == temp1:
                    continue
                temp1.neighbor.append(x)  # 初始化邻居信息
            except StopIteration:  # 遇到StopIteration就退出循环
                break
    # 初始化节点路由表
    j = 0
    while j < len(node):
        for N in node:
            if N == node[j]:
                continue
            else:
                shortest_path = nx.shortest_path(G, node[j], N)
                node[j].route_table[shortest_path[-1].mac] = shortest_path[1].mac
        j += 1
    #对拓扑进行子网划分（目前是划分为8个社区）
    partition = community.best_partition(G, random_state=1)
    nodes_community = list()
    for com in set(partition.values()):
        list_nodes = [nodes for nodes in partition.keys()
                      if partition[nodes] == com]
        nodes_community.append(list_nodes)
    SUBNET_LIST = list()
    i = 0
    while i < len(nodes_community):
        if i == 0:
            Net = Subnet(Type.subnet_1)
        if i == 1:
            Net = Subnet(Type.subnet_2)
        if i == 2:
            Net = Subnet(Type.subnet_3)
        if i == 3:
            Net = Subnet(Type.subnet_4)
        if i == 4:
            Net = Subnet(Type.subnet_5)
        if i == 5:
            Net = Subnet(Type.subnet_6)
        if i == 6:
            Net = Subnet(Type.subnet_7)
        if i == 7:
            Net = Subnet(Type.subnet_8)
        for n in nodes_community[i]:
            n.type = Net.type
            Net.node_list.append(n)
        i+=1
        SUBNET_LIST.append(Net)
    return G, SUBNET_LIST  # 返回拓扑图和子网列表


def find_net(node, SUBNET_LIST):  # 判断节点属于哪个子网
    for net in SUBNET_LIST:
        if net.type == node.type:
            return net


def find_e_subnet(e, subnet):  # 唤醒子网中相应的事件监视器
    for temp_e in subnet.incoming_event_monitor:
        if temp_e.first_hop.mac == e.first_hop.mac and temp_e.next_hop.mac == e.next_hop.mac:
            return temp_e
    for temp_e in subnet.outcoming_event_monitor:
        if temp_e.first_hop.mac == e.first_hop.mac and temp_e.next_hop.mac == e.next_hop.mac:
            return temp_e
    for temp_e in subnet.internal_event_monitor:
        if temp_e.first_hop.mac == e.first_hop.mac and temp_e.next_hop.mac == e.next_hop.mac:
            return temp_e
    return False

def find_e_node(e, node): #唤醒节点中相应的事件监视器
    for temp_e in node.in_event_monitor:
        if temp_e.first_hop.mac == e.first_hop.mac and temp_e.next_hop.mac == e.next_hop.mac:
            return temp_e
    for temp_e in node.out_event_monitor:
        if temp_e.first_hop.mac == e.first_hop.mac and temp_e.next_hop.mac == e.next_hop.mac:
            return temp_e

if __name__ == '__main__':
    G, SUBNET_LIST = manet_generator()
    for net in SUBNET_LIST:
        print("子网：",net.type)
        print(net.incoming_event_monitor)
        print(net.outcoming_event_monitor)
        print(net.internal_event_monitor)
        print("*************")
    node = list(G.nodes())
    print(node)
    for N in node:
        print('node: ', N, '\t', N.neighbor)
    for N in node:
        print('node: ', N, '\t', N.route_table)
    e2 = Event_monitor(node[0], node[2])
    temp_e1 = find_e_node(e2,node[0])
    temp_e2 = find_e_node(e2,node[2])
    temp_e1.message_pool.append("hello world!!!")
    # temp_e2 = find_e_subnet(e2,subnet=SUBNET_LIST[0])
    temp_e2.message_pool.append("hello world!!!")
    for N in node:
        print('node: ',N,'\tin_event:',N.in_event_monitor)
        print('node: ',N,'\tout_event:',N.out_event_monitor)
    for net in SUBNET_LIST:
        print("子网：",net.type)
        print(net.incoming_event_monitor)
        print(net.outcoming_event_monitor)
        # print(net.internal_event_monitor)
        print("*************")
