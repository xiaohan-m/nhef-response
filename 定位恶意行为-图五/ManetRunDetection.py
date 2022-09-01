# @Time     :2021/10/9 17:42
# @Author   :pc chen

# 每个节点都会有相应的指标数据
# 每个节点都需要有流的池：进入的和出去的
# 每个节点都统计1000个数据流应该就可以吧
# 然后先统计每个节点的数据，然后再根据子网划分，选择之前的三个子网，将数据的颜色记录
# 需要写一个函数，计算每个节点的指标

"""
考虑错误转发路径
"""
import copy
import math
from datetime import datetime
import random

import community
import matplotlib
import networkx as nx
import simpy
import xlsxwriter
from matplotlib import pyplot as plt
from matplotlib.patches import Ellipse

from DataIndex import DataIndex
from network.ManetTopology import manet_generator
from network.Package import Package

# global 变量
from network.Stream import Stream

PACKAGE_ID = 1  # 用来记录数据包的编号
TRAFFIC_LOAD = 1  # 系统强度(每个时隙产生正常数据包的概率)
SLOT_NUM = 20000

SEND_STREAM_POOL = list()
RECEIVE_STREAM_POOL = list()
COMPLETE_RECEIVE_STREAM_POOL = list()
STREAM_ID = 1
STREAM_SIZE = 10
PACKAGE_LOSS_RATE = 0.0005

# 固定两个恶意节点
M_new_add = 19  # 发动新增数据包的恶意行为节点node_list[19]:6453

M_new_add_rate = 0.01
M_wrong_path = 26  # 发动恶意丢包的恶意行为节点node_list[26]:11537
M_wrong_path_rate = 0.01

# 增加两个恶意节点
M_new_add_2 = 33  # 发动新增数据包的恶意行为节点node_list[33]:3333
M_new_add_rate_2 = 0.001
M_wrong_path_2 = 12  # 发动恶意丢包的恶意行为节点node_list[12]:5006
M_wrong_path_rate_2 = 0.001


def sim_run(node_list):
    # 接下来是每个时隙都要干的事情
    global SLOT_NUM, M_new_add, M_wrong_path
    slot = 1
    while True:
        flag = 0
        if slot % 10000 == 0:
            print('当前仿真间隙：', slot)
            print("M_new_add:%s" % len(node_list[M_new_add].full_receive_stream_pool))
            print("M_new_add_2:%s" % len(node_list[M_new_add_2].full_receive_stream_pool))
            print("M_wrong_path:%s" % len(node_list[M_wrong_path].full_receive_stream_pool))
            print("M_wrong_path_2:%s" % len(node_list[M_wrong_path_2].full_receive_stream_pool))
        if len(node_list[M_new_add].full_receive_stream_pool) > 5000 and len(
                node_list[M_wrong_path].full_receive_stream_pool) > 5000 and len(
            node_list[M_new_add_2].full_receive_stream_pool) > 5000 and len(
            node_list[M_wrong_path_2].full_receive_stream_pool) > 5000:
            break
        # 输出每个节点的流的数量
        generate_message(node_list)
        # generate_new_add_packet(node_list)
        # 对每个节点判断自己的发送池中是否有消息需要转发
        # 完成消息传输
        tran_results = transmission_package(node_list)
        slot += 1
        # 下一个时隙完成消息接收
        receiving_package(node_list, tran_results)


# 根据系统强度生成正常数据包
# 根据系统强度生成正常数据包
def generate_message(node_list):
    # 这里暂时考虑简单一点，只考虑外部节点之间互相发送消息
    global PACKAGE_ID, TRAFFIC_LOAD
    t = random.random()
    # 根据系统强度产生一个新的消息(考虑p<=1)
    if t <= TRAFFIC_LOAD:
        caller = random.randint(0, len(node_list) - 1)
        while True:
            receiver = random.randint(0, len(node_list) - 1)
            if receiver == caller:
                continue
            else:
                break
        # 随机选择了两个外部节点，此时需要造一个package对象
        new_package = Package(id=PACKAGE_ID, caller_id=node_list[caller].mac,
                              receiver_id=node_list[receiver].mac)  # 数据包(数据包编号，发送节点id，接收节点id)
        # 将数据包与流产生联系
        generate_in_stream(new_package, node_list[caller])
        # 将包裹放入，发送消息池
        node_list[caller].buffer_message_pool.append(new_package)
        PACKAGE_ID += 1
        return True
    else:
        return None


# def generate_new_add_packet(node_list):  # 新增恶意数据包
#     global PACKAGE_ID, M_new_add, M_new_add_rate, STREAM_ID, STREAM_SIZE
#     # 以概率mp产生一个新的消息
#     if random.random() < M_new_add_rate:
#         while True:
#             R = random.randint(0, len(node_list) - 1)
#             if R == M_new_add:
#                 continue
#             else:
#                 break
#         # 随机选择了子网A中的一个节点，与其它任意一个非子网A中的节点
#         # 产生一个新的数据包裹，并对包裹进行初始化
#         new_package = Package(id=PACKAGE_ID, caller_id=node_list[M_new_add].mac,
#                               receiver_id=node_list[R].mac)  # 数据包(数据包编号，发送节点id，接收节点id)
#         new_package.new_add_status = 1
#         # 将包裹放入，发送消息池
#         node_list[M_new_add].buffer_message_pool.append(new_package)
#         for stream in node_list[M_new_add].send_stream_pool:
#             if (stream.caller_id == new_package.caller_id and stream.receiver_id == new_package.receiver_id):
#                 new_package.stream_id = stream.id
#                 break
#         if new_package.stream_id == -1:
#             new_stream = Stream(STREAM_ID, new_package.caller_id, new_package.receiver_id, STREAM_SIZE)
#             new_package.stream_id = new_stream.id
#             node_list[M_new_add].send_stream_pool.append(new_stream)
#         PACKAGE_ID += 1
#         return True
#     else:
#         return None


# def is_belongs_to_net(node, net):
#     return node.type == net.type


# 产生流
def generate_in_stream(package, node):
    new_package = copy.copy(package)
    global STREAM_ID
    # 首先判断是否需要新建流
    for stream in node.send_stream_pool:
        if (stream.caller_id == package.caller_id and stream.receiver_id == package.receiver_id):
            stream.package_list.append(new_package)
            package.stream_id = stream.id
            new_package.stream_id = stream.id
            if (len(stream.package_list) == stream.size):
                # 如果流的数据包数量已经达到最大，则从发送流中移除，减少后续判断时间
                node.send_stream_pool.remove(stream)
                node.full_send_stream_pool.append(stream)
            return True
    #  如果已经发送的流里面没有对应的流的信息，则需要新建流
    new_stream = Stream(STREAM_ID, package.caller_id, package.receiver_id, STREAM_SIZE)
    new_stream.package_list.append(new_package)
    package.stream_id = new_stream.id
    new_package.stream_id = new_stream.id
    node.send_stream_pool.append(new_stream)
    STREAM_ID += 1


# 产生流
def generate_out_stream(package, node):
    new_package = copy.copy(package)
    # 首先判断是否需要新建流
    for stream in node.receive_stream_pool:
        if (stream.id == package.stream_id):
            stream.package_list.append(new_package)
            if (len(stream.package_list) == stream.size):
                node.full_receive_stream_pool.append(stream)
                node.receive_stream_pool.remove(stream)
            return True
    new_stream = Stream(package.stream_id, package.caller_id, package.receiver_id, STREAM_SIZE)
    new_stream.package_list.append(new_package)
    node.receive_stream_pool.append(new_stream)
    return True


# 完成消息的转发
def transmission_package(node):
    t_value = list()
    for N in node:
        t_value.append(N.transport_message())
    return t_value


# 完成消息的接收
def receiving_package(node_list, tran_results):
    global PACKAGE_LOSS_RATE, M_wrong_path, M_wrong_path_rate, M_new_add, M_new_add_rate, M_wrong_path_2, M_wrong_path_rate_2, M_new_add_2, M_new_add_rate_2
    k = 0
    while k < len(tran_results):
        if tran_results[k] == None:
            k += 1
            continue
        else:
            # 按照路由表转发的方式，让下一跳节点接收消息
            new_package = tran_results[k]
            # 加入自然丢包
            if k == M_wrong_path and random.random() < M_wrong_path_rate:
                new_package.wrong_path_status = 1
            if k == M_wrong_path_2 and random.random() < M_wrong_path_rate_2:
                new_package.wrong_path_status = 1
            if k == M_new_add and random.random() < M_new_add_rate:
                new_package.new_add_status = 1
            if k == M_new_add_2 and random.random() < M_new_add_rate_2:
                new_package.new_add_status = 1
            if random.random() < PACKAGE_LOSS_RATE:
                new_package.loss_status = 1
            generate_out_stream(new_package, node_list[k])
            new_package.new_add_status = -1
            new_package.loss_status = -1
            new_package.wrong_path_status = -1
            if new_package.receiver_id == node_list[k].mac:
                k += 1
                continue
            if new_package.receiver_id in node_list[k].route_table:
                for N in node_list:
                    if N.mac == node_list[k].route_table[new_package.receiver_id]:  # 按照路由表的方式对数据包进行接收
                        # 下一跳的进入检测也是要检测一下的
                        N.receive_message(new_package)
            k += 1


def clear_net(node_list):
    global SEND_STREAM_POOL, RECEIVE_STREAM_POOL, COMPLETE_RECEIVE_STREAM_POOL
    for node in node_list:
        node.clear()
    SEND_STREAM_POOL = list()
    RECEIVE_STREAM_POOL = list()
    COMPLETE_RECEIVE_STREAM_POOL = list()


def statistics_index(node):
    stream_type_green2green = 0
    stream_type_green2red = 0
    stream_type_red2green = 0
    stream_type_red2red = 0
    for out_stream in node.full_receive_stream_pool:
        # print("size:%s" % out_stream.size)
        out_only_nature_loss_package_num = 0
        out_only_wrong_path_package_num = 0
        out_only_new_add_package_num = 0
        out_new_add_and_loss_package_num = 0
        out_wrong_path_and_loss_package_num = 0
        out_other_package_num = 0
        for out_package in out_stream.package_list:
            if out_package.wrong_path_status == -1 and out_package.loss_status == 1:
                out_only_nature_loss_package_num += 1
            if out_package.wrong_path_status == 1 and out_package.loss_status == -1:
                out_only_wrong_path_package_num += 1
            if out_package.loss_status == -1 and out_package.new_add_status == 1:
                out_only_new_add_package_num += 1
            if out_package.loss_status == 1 and out_package.new_add_status == 1:
                out_new_add_and_loss_package_num += 1
            if out_package.loss_status == 1 and out_package.wrong_path_status == 1:
                out_wrong_path_and_loss_package_num += 1
                # print("out_new_add_and_loss_package_num:%s" % out_new_add_and_loss_package_num)
            else:
                out_other_package_num += 1
        if out_only_new_add_package_num > 0 or out_only_wrong_path_package_num > 0 or out_wrong_path_and_loss_package_num > 0:
            stream_type_red2red += 1
        elif out_only_nature_loss_package_num > 0 and out_new_add_and_loss_package_num == 0:
            stream_type_green2red += 1
        elif out_only_nature_loss_package_num == 0 and out_new_add_and_loss_package_num > 0:
            stream_type_red2green += 1
        else:
            # print("%s,%s,%s,%s,%s" % (
            # out_only_nature_loss_package_num, out_only_wrong_path_package_num, out_only_new_add_package_num,
            # out_new_add_and_loss_package_num, out_wrong_path_and_loss_package_num))
            stream_type_green2green += 1

    # 到这里就算把所有接收到的流的类型确定了，下面是计算具体的指标
    TP = stream_type_red2red  # 真阳性的数量
    FP = stream_type_green2red  # 假阳性
    FN = stream_type_red2green  # 假阴性的数量
    TN = stream_type_green2green  # 真阴性的数量
    # print("node:%s"%node.mac+"\tTP:%s"%TP+"\tFP:%s"%FP+"\tFN:%s"%FN+"\tTN:%s"%TN)
    if TP != 0:
        node.jaccard = TP / (TP + FP + FN)
        node.fm = math.sqrt((TP / (TP + FP)) * (TP / (TP + FN)))
        node.randIndex = (TP + TN) / (TP + FP + FN + TN)
    if TP == 0:
        node.jaccard = 0
        node.fm = 0
        node.randIndex = 1


def output_data(dataIndexList):
    global SLOT_NUM, ROUND_NUM
    now = datetime.now()
    s1 = now.strftime("%Y_%m%d_%H%M")
    workbook = xlsxwriter.Workbook('..\data_record\错误转发路径\数据统计%s.xlsx' % s1, {'nan_inf_to_errors': True})
    worksheet1 = workbook.add_worksheet('data_record')
    worksheet1.write(0, 0, "恶意程度")
    worksheet1.write(0, 1, "green2green")
    worksheet1.write(0, 2, "green2red")
    worksheet1.write(0, 3, "red2green")
    worksheet1.write(0, 4, "red2red")
    worksheet1.write(0, 5, "统计的流的数量")
    worksheet1.write(0, 6, "Jaccard指数")
    worksheet1.write(0, 7, "FM指数")
    worksheet1.write(0, 8, "Rand index")

    i = 0
    while i < len(dataIndexList):
        worksheet1.write(i + 1, 0, dataIndexList[i].mp)
        worksheet1.write(i + 1, 1, dataIndexList[i].green2green)
        worksheet1.write(i + 1, 2, dataIndexList[i].green2red)
        worksheet1.write(i + 1, 3, dataIndexList[i].red2green)
        worksheet1.write(i + 1, 4, dataIndexList[i].red2red)
        worksheet1.write(i + 1, 5, dataIndexList[i].size)
        worksheet1.write(i + 1, 6, dataIndexList[i].jaccard)
        worksheet1.write(i + 1, 7, dataIndexList[i].fm)
        worksheet1.write(i + 1, 8, dataIndexList[i].randIndex)
        i += 1
    worksheet1.write(i + 1, 0, "数据流中数据包的个数:%s" % STREAM_SIZE)
    worksheet1.write(i + 2, 0, "自然丢包率:%s" % PACKAGE_LOSS_RATE)
    worksheet1.write(i + 3, 0, "系统强度:%s" % TRAFFIC_LOAD)
    workbook.close()


def draw_topology(G, node_list):
    nodes = list(G.nodes())
    for N in nodes:
        G.add_node(N, value='%.2f' % N.jaccard)
    partition = community.best_partition(G, random_state=1)
    # size = float(len(set(partition.values())))
    nodes_community = list()
    for com in set(partition.values()):
        list_nodes = [nodes for nodes in partition.keys()
                      if partition[nodes] == com]
        nodes_community.append(list_nodes)
    fig = plt.figure(figsize=(10, 7))
    plt.rc('font', family='Times New Roman')
    ax = fig.add_subplot(111)
    ax.set(xlim=[5, 23], ylim=[13, 23.2], title='An Example Axes')
    g = nx.subgraph(G, nodes_community[0] + nodes_community[2] + nodes_community[5] + nodes_community[6])
    # 再取一个
    node_labels = nx.get_node_attributes(g, 'value')
    position_1 = [[16.2, 17], [19.2, 17], [16.5, 15.3], [18.2, 16.5], [17.7, 15.5], [15.2, 15.5], [19.7, 15.5],
                  [21.2, 16]]
    position_2 = [[18, 20], [15, 20], [17, 21], [21, 19.85], [21.5, 20.48], [20, 19.5], [21.4, 21.2], [18, 21.2],
                  [19.5, 21], [16, 22], [19.5, 22]]
    position_3 = [[13, 16.5], [9.5, 17], [9, 18.5], [7, 18], [10.5, 16], [11, 18], [9, 15], [11, 15], [6.5, 17],
                  [7, 16]]
    position_4 = [[10.5, 20.2], [6.2, 21.4], [7.9, 22], [9, 21.1], [7.3, 20.5], [10, 22], [11.4, 21.2],
                  [6.1, 13.7], [6, 11.7], [6, 17.7]]
    # 加一个子网，然后重新布局
    pos = dict()
    i = 0
    while i < len(nodes_community[0]):
        nodes_community[0][i].position = position_1[i]
        pos[nodes_community[0][i]] = position_1[i]
        i += 1
    i = 0
    while i < len(nodes_community[2]):
        nodes_community[2][i].position = position_2[i]
        pos[nodes_community[2][i]] = position_2[i]
        i += 1
    i = 0
    while i < len(nodes_community[5]):
        nodes_community[5][i].position = position_3[i]
        pos[nodes_community[5][i]] = position_3[i]
        i += 1
    i = 0
    while i < len(nodes_community[6]):
        nodes_community[6][i].position = position_4[i]
        pos[nodes_community[6][i]] = position_4[i]
        i += 1
    # for n in nodes_community[5]:
    #     print(n)
    print(nodes_community[6])
    # 加pos
    # nx.draw_networkx(g, pos, with_labels=False)
    cmap = plt.get_cmap('cool')  # 可以选要提取的cmap，如'Spectral'
    # cNorm = matplotlib.colors.Normalize(0, 1)
    for n in g.nodes():
        # if n.color_value[0] > 1 or n.color_value[1] > 1 or n.color_value[2] > 1:
        #     print('n.color_value:', n.color_value)
        # if n.color_value > 0.5:
        #     n.color_value -= 0.1
        # if n.color_value < 0.5:
        #     n.color_value += 0.1
        if n in nodes_community[0]:
            nx.draw_networkx_nodes(g, pos, [n], node_color=[cmap(n.jaccard)], node_shape="o", node_size=800,
                                   edgecolors='k')
        elif n in nodes_community[2]:
            nx.draw_networkx_nodes(g, pos, [n], node_color=[cmap(n.jaccard)], node_shape="o", node_size=800,
                                   edgecolors='k')
        elif n in nodes_community[5]:
            nx.draw_networkx_nodes(g, pos, [n], node_color=[cmap(n.jaccard)], node_shape="o", node_size=800,
                                   edgecolors='k')
        elif n in nodes_community[6]:
            nx.draw_networkx_nodes(g, pos, [n], node_color=[cmap(n.jaccard)], node_shape="o", node_size=800,
                                   edgecolors='k')
    new_g = nx.Graph(g)
    nx.draw_networkx_labels(new_g, pos, labels=node_labels, font_color='k', font_size=8, alpha=1)
    nx.draw_networkx_labels(new_g, pos, labels={nodes_community[2][1]: '%.2f' % nodes_community[2][1].jaccard,
                                                nodes_community[5][4]: '%.2f' % nodes_community[5][4].jaccard,
                                                nodes_community[0][1]: '%.2f' % nodes_community[0][1].jaccard,
                                                nodes_community[6][0]: '%.2f' % nodes_community[6][0].jaccard,
                                                },
                            font_color='white', font_size=8, alpha=1)
    node_remove_list = [8047, 4129, 7914, 11090, 11812]
    for n in nodes:
        if n.mac in node_remove_list:
            new_g.remove_edge(n, n)
    nx.draw_networkx_edges(new_g, pos)
    ellipse_A = Ellipse((18, 16.1), width=7.8, height=3.7, alpha=0.2, color='#DB7093')
    ellipse_B = Ellipse((18, 20.7), width=8.8, height=3.8, alpha=0.2, color='#eb8e55')
    ellipse_C = Ellipse((9.7, 16.7), width=8.4, height=4.5, alpha=0.2, color='#9370DB')
    ellipse_D = Ellipse((9, 21.1), width=7, height=3.4, alpha=0.2, color='#87ceeb')
    # circle_B = Circle(xy=(19.5, 18), radius=2.6, alpha=0.2, color='#073763')
    # circle_C = Circle(xy=(9.5, 16), radius=2.6, alpha=0.2, color='#674ea7')
    ax.add_patch(ellipse_A)
    ax.add_patch(ellipse_B)
    ax.add_patch(ellipse_C)
    ax.add_patch(ellipse_D)
    now = datetime.now()
    s1 = now.strftime("%Y_%m%d_%H%M")
    # plt.text(5.5, 20.7, "Unexpected generating:%s" % MP, fontsize=12, wrap=True)
    # plt.text(5.5, 20.4, "Incorrect forwarding:%s" % ML, fontsize=12, wrap=True)
    # plt.text(5.5, 20.7, "Unexpected generating:%s" % MP, fontsize=12, wrap=True)
    # plt.text(5.5, 20.4, "Incorrect forwarding:%s" % ML, fontsize=12, wrap=True)
    # plt.text(5.5, 20.7, "Unexpected generating:%s" % MP, fontsize=12, wrap=True)
    # plt.text(5.5, 20.4, "Incorrect forwarding:%s" % ML, fontsize=12, wrap=True)
    # plt.text(5.5, 20.6, "Input Detection Effectiveness:%s" % in_detection_p, fontsize=12, wrap=True)
    # plt.text(5.5, 20.2, "Output Detection Effectiveness:%s" % out_detection_p, fontsize=12, wrap=True)
    # plt.savefig('.\data record\Figure_6_data_record\图6_%s.svg'%s1)
    # plt.annotate(' Malicious node\nwith threats 2-4', fontsize=12, xy=(14.7, 18.2), xytext=(9.8, 19.2),
    #              arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
    # plt.annotate(' Malicious node\nwith threats 1&6', fontsize=12, xy=(10.3, 15.7), xytext=(7.5, 13.5),
    #              arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
    plt.annotate('Incorrect forwarding\n(Threats 1&6)\nMalicious:0.01', fontsize=12, xy=(14.8, 20.3), xytext=(12.4, 22),
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
    plt.text(15.45, 19.65, "Node #11537", fontsize=12, color="red",wrap=True)

    plt.annotate('Unexpected packets\n(Threats 2-4)\nMalicious:0.001', fontsize=12, xy=(10.1, 20.1), xytext=(5.5, 19),
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
    plt.text(11, 20.1, "Node #3333", fontsize=12,  color="red",wrap=True)

    plt.annotate('Unexpected packets\n(Threats 2-4)\nMalicious:0.01', fontsize=12, xy=(10.1, 15.9), xytext=(5.5, 14.5),
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
    plt.text(8.1, 16, "Node #6453", fontsize=12,color="red", wrap=True)

    plt.annotate('Incorrect forwarding\n(Threats 1&6)\nMalicious:0.001', fontsize=12, xy=(19.6, 17.2), xytext=(19.6, 17.9),
                 arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
    plt.text(19.8, 16.9, "Node #5006", fontsize=12,color="red", wrap=True)

    # ax2 = plt.axes([0.84, 0.12, 0.02, 0.3])
    # cb = matplotlib.colorbar.ColorbarBase(ax2, norm=cNorm, cmap=cmap, orientation="vertical", ticklocation='right',
    #                                       ticks=[0, 0.5, 1], label="Maliciousness")
    # cb.set_label("Maliciousness")
    plt.show()
    # # fig.subplots_adjust(bottom=0.5)
    # # plt.colorbar(scalarMap,
    # #              cax=ax, orientation='vertical', label='Some Units')


if __name__ == '__main__':
    G, SUBNET_LIST = manet_generator()
    node_list = list(G.nodes())
    in_detection_p = 1
    out_detection_p = 1
    dataIndexList = list()
    sim_run(node_list)

    for node in node_list:
        # 计算出每个节点的流的类型数量，然后计算节点相应的指标值
        statistics_index(node)
        # 统计完指标就可以进行绘图了
    draw_topology(G, node_list)
