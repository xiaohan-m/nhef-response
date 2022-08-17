# @Time     :2021/10/9 17:42
# @Author   :pc chen


"""
固定每轮仿真时隙：500
考虑不同的检测概率下，检测成功率与恶意程度之间的关系
恶意攻击的方式为：新增数据包
只考虑子网A，如果子网A出去的数据包中flag为False则意味着检测出来了
"""
import copy
from datetime import datetime
import random
import sys

import gevent
import numpy as np
import simpy
import xlsxwriter
from matplotlib import pyplot as plt
from matplotlib.pyplot import plot
from numpy import log10

from network.Event_monitoring import Event_monitor
from network.ManetNode import Type, ManetNode
from network.ManetTopology import manet_generator, find_net, find_e_subnet, find_e_node
from network.Package import Package
from multiprocessing import Pool

# global 变量
PACKAGE_ID = 1  # 用来记录数据包的编号
TRAFFIC_LOAD = 0.2  # 系统强度(每个时隙产生正常数据包的概率)
MALICIOUE_PACKAGE_POOL = list()
SLOT_NUM = 500
ROUND_NUM = 1000


def sim_run(env, node_list, SUBNET_LIST, in_detection_p, out_detection_p,mp):
    # 接下来是每个时隙都要干的事情
    global SLOT_NUM
    while True:
        if env.now == SLOT_NUM:
            # print('当前仿真间隙：', env.now, "当前检测概率：", dp, "当前节点恶意程度:", mp)
            break
        # if env.now % 500 == 0:
        #     print('当前仿真间隙：', env.now, "当前检测概率：", dp, "当前节点恶意程度:", mp)
        #     # 每个时隙开始之前根据系统强度生成新的消息
        #     # 目前考虑简单一些，外部节点之间互相发送消息
        generate_message(node_list,in_detection_p)
        generate_leaked_packet(node_list, SUBNET_LIST, mp)
        # 对每个节点判断自己的发送池中是否有消息需要转发
        # 完成消息传输
        tran_results = transmission_package(node_list)
        yield env.timeout(1)
        # 下一个时隙完成消息接收
        receiving_package(node_list, tran_results, in_detection_p, out_detection_p)


# 根据系统强度生成正常数据包
# 根据系统强度生成正常数据包
def generate_message(node_list,in_detection_p):
    # 这里暂时考虑简单一点，只考虑外部节点之间互相发送消息
    global PACKAGE_ID, TRAFFIC_LOAD,TOTAL_TRAN_NUM
    t = random.random()
    # 根据系统强度产生一个新的消息(考虑p<=1)
    if t <= TRAFFIC_LOAD:
        caller = random.randint(0, len(node_list) - 1)
        while True:
            receiver = random.randint(0, len(node_list) - 1)
            if receiver == caller or node_list[receiver] in node_list[caller].neighbor:
                continue
            else:
                break
        # 随机选择了两个外部节点，此时需要造一个package对象
        # 产生一个新的数据包裹，并对包裹进行初始化
        new_package = Package(id=PACKAGE_ID, caller_id=node_list[caller].mac,
                              receiver_id=node_list[receiver].mac)  # 数据包(数据包编号，发送节点id，接收节点id)
        new_package.message = 'message%s' % PACKAGE_ID  # 初始化数据包内容
        # 将包裹放入，发送消息池
        node_list[caller].buffer_message_pool.append(new_package)
        node_list[caller].qs_buffer_message_pool.add(new_package.id)
        if random.random() < in_detection_p:
            super_node = ManetNode(mac=0, type=Type.external)  # 只是用来统计正常新增的数据包
            e = Event_monitor(super_node, node_list[caller])  # 看上去好像是超级节点发给节点caller的
            in_e = find_e_node(e,node_list[caller])
            in_e.message_pool.append(new_package)
        PACKAGE_ID += 1
        return True
    else:
        return None


def is_belongs_to_net(node, net):
    return node.type == net.type


# 完成消息的转发
def transmission_package(node):
    t_value = list()
    for N in node:
        t_value.append(N.transport_message())
    return t_value


# 完成消息的接收
def receiving_package(node_list, tran_results, in_detection_p, out_detection_P):
    k = 0
    while k < len(tran_results):
        if tran_results[k] == None:
            k += 1
            continue
        else:
            # 按照路由表转发的方式，让下一跳节点接收消息
            new_package = tran_results[k]
            if new_package.head[1] == node_list[k].mac:
                #说明是需要发送给0号节点的！！！
                super_node = ManetNode(mac=0, type=Type.external)  # 只是用来统计正常新增的数据包
                temp_e = Event_monitor(node_list[k], super_node)  # 生成一个事件监视器
                out_e = find_e_node(temp_e, node_list[k])
                # 对于发送数据包，以出口检测概率out_detection_p进行检测
                if random.random() < out_detection_P:
                    out_e.message_pool.append(new_package)
                k+=1
                continue
            if new_package.head[1] in node_list[k].route_table:
                for N in node_list:
                    if N.mac == node_list[k].route_table[new_package.head[1]]:  # 按照路由表的方式对数据包进行接收
                        N.receive_message(new_package)
                        temp_e = Event_monitor(node_list[k], N)  # 生成一个事件监视器
                        # 这里是node[k]发送数据包，N接收数据包
                        out_e = find_e_node(temp_e,node_list[k])
                        # 对于发送数据包，以出口检测概率out_detection_p进行检测
                        if random.random() < out_detection_P:
                            out_e.message_pool.append(new_package)
                        in_e = find_e_node(temp_e,N)
                        # 对于接收数据包，以入口检测概率in_detection_p进行检测
                        if random.random() < in_detection_p:
                            in_e.message_pool.append(new_package)
            k += 1


# 这里用于定义一种恶意行为：子网A中随机产生一个恶意节点以一定的概率产生恶意数据包发给网络中任意一个节点
def generate_leaked_packet(node_list, SUBNET_LIST, mp):
    global PACKAGE_ID, MALICIOUE_PACKAGE_POOL
    t = random.random()
    # 以概率mp产生一个新的消息(考虑p<=1)
    if t <= mp:
        C = random.randint(0, len(SUBNET_LIST[0].node_list) - 1)
        while True:
            R = random.randint(0, len(node_list) - 1)
            if node_list[R].type.value == SUBNET_LIST[0].node_list[C].type.value:
                continue
            else:
                break
        # 随机选择了子网1中的一个节点，与其它任意一个非子网1中的节点
        # 产生一个新的数据包裹，并对包裹进行初始化
        new_package = Package(id=PACKAGE_ID, caller_id=SUBNET_LIST[0].node_list[C].mac,
                              receiver_id=node_list[R].mac)  # 数据包(数据包编号，发送节点id，接收节点id)
        new_package.message = 'message%s' % PACKAGE_ID  # 初始化数据包内容
        new_package.flag = False
        MALICIOUE_PACKAGE_POOL.append(new_package)
        # new_package.timestamp.append(current_slot)
        # 将包裹放入，发送消息池
        SUBNET_LIST[0].node_list[C].buffer_message_pool.append(new_package)
        PACKAGE_ID += 1
        return True
    else:
        return None


# 检测函数
def monitoring_results(subnet):
    # print(subnet.incoming_event_monitor)
    # print(subnet.outcoming_event_monitor)
    for e in subnet.outcoming_event_monitor:  # 只需要对出口数据包进行监测
        if len(e.message_pool) > 0:
            for package in e.message_pool:
                if package.flag == False:  # 检查到了错误的数据包,返回1
                    return 1
    return 0


def clear_net(node, SUBNET_LIST):
    for n in node:
        n.clear()
    for net in SUBNET_LIST:
        net.clear_event()


def statistics_function(node_list, SUBNET_LIST, in_detection_p, out_detection_p, mp_list):
    global ROUND_NUM
    successful_p = list()
    # 这里之后可以考虑采用线程池的方式进行
    for mp in mp_list:
        results = list()
        i = 0
        while i < ROUND_NUM:
            results.append(env_run(node_list, SUBNET_LIST, in_detection_p, out_detection_p, mp))
            # for net in SUBNET_LIST:
            #     net.clear_event()
            for n in node_list:
                n.clear()
            # print(i)
            i += 1
        successful_p.append(sum(results) / len(results))
        print("mp:", mp)
    return successful_p


def env_run(node_list, SUBNET_LIST, in_detection_p, out_detection_p, mp):
    env = simpy.Environment()
    env.process(sim_run(env, node_list, SUBNET_LIST, in_detection_p, out_detection_p,mp))
    env.run()
    return monitoring_results(SUBNET_LIST[0])  # 返回一轮检测的结果


# 对于每个检测概率：考虑采取不同的产生错误数据包的概率（恶意程度）
# 衡量在不同的恶意程度下，检测成功率

def output_data(detection_p, malicious_p, Detection_success_rate):
    global SLOT_NUM, ROUND_NUM
    now = datetime.now()
    s1 = now.strftime("%Y_%m%d_%H%M")
    workbook = xlsxwriter.Workbook('.\data record\Figure_1_data_record\数据统计%s.xlsx' % s1, {'nan_inf_to_errors': True})
    worksheet1 = workbook.add_worksheet('data_record')
    worksheet1.write(0, 0, "恶意程度")
    i = 0
    while i < len(malicious_p):
        worksheet1.write(i + 1, 0, malicious_p[i])
        i += 1
    j = 0
    while j < len(detection_p):
        worksheet1.write(0, j + 1, "检测成功率（检测概率为：%s)" % detection_p[j])
        k = 0
        while k < len(Detection_success_rate[j]):
            worksheet1.write(k + 1, j + 1, Detection_success_rate[j][k])
            k += 1
        j += 1
    worksheet1.write(i + 1, 0, "Slot_num:%s" % SLOT_NUM)
    worksheet1.write(i + 2, 0, "Round_num:%s" % ROUND_NUM)
    worksheet1.write(i + 3, 0, "Topology:103个节点8个子网")
    workbook.close()


if __name__ == '__main__':
    # G, SUBNET_LIST = manet_generator()
    # node = list(G.nodes())
    # 这里想用多线程的方式来进行循环
    # 首先假设考虑一个监视概率p，一共跑100次实验，每次试验的时隙长度为1000，看这100次实验中，有多少次检测到了恶意节点
    # 出口检测概率
    out_detection_p_list = np.arange(0.1, 1.01, 0.1)  # 检测概率
    in_detection_p = 1
    # malicious_p = np.arange(0, 0.1, 0.01)  # 恶意程度
    malicious_p = np.logspace(log10(0.0001), log10(0.1), 20)
    Detection_success_rate = list()  # 检测成功率
    process_pool = Pool(len(out_detection_p_list))  # 生成进程池
    t = []
    for out_detection_p in out_detection_p_list:  # 对于每个检测概率，采用一个进程
        G, SUBNET_LIST = manet_generator()
        node = list(G.nodes())
        res = process_pool.apply_async(statistics_function,
                                       args=(node, SUBNET_LIST, in_detection_p, out_detection_p, malicious_p))  # apply_sync的结果就是异步获取func的返回值
        t.append(res)
    for g in t:
        Detection_success_rate.append(g.get())
    # 调用数据输出函数
    print(Detection_success_rate)
    output_data(out_detection_p_list, malicious_p, Detection_success_rate)
