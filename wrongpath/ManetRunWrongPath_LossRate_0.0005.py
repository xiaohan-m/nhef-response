# @Time     :2021/10/9 17:42
# @Author   :pc chen


"""
考虑错误转发路径
"""
import math
from datetime import datetime
import random
import simpy
import xlsxwriter

from DataIndex import DataIndex
from network.ManetTopology import manet_generator, find_net, find_e_subnet, find_e_node
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


def sim_run(env, node_list, wrongPathRate):
    # 接下来是每个时隙都要干的事情
    global SLOT_NUM
    while True:
        if env.now % 10000 == 0:
            print('当前仿真间隙：', env.now)
        if len(COMPLETE_RECEIVE_STREAM_POOL) >= 5000:
            # print('当前仿真间隙：', env.now, "当前检测概率：", dp, "当前节点恶意程度:", mp)
            break
        generate_message(node_list)
        # 对每个节点判断自己的发送池中是否有消息需要转发
        # 完成消息传输
        tran_results = transmission_package(node_list)
        yield env.timeout(1)
        # 下一个时隙完成消息接收
        receiving_package(node_list, tran_results, wrongPathRate)


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
        generate_send_stream(new_package)
        # 将包裹放入，发送消息池
        node_list[caller].buffer_message_pool.append(new_package)
        # if random.random() < in_detection_p:
        #     # 说明数据包在进入网络的时候被检测到了，此时可以给数据包加一个标记
        #     new_package.in_status = 1
        #     # super_node = ManetNode(mac=0, type=Type.external)  # 只是用来统计正常新增的数据包
        #     # e = Event_monitor(super_node, node_list[caller])  # 看上去好像是超级节点发给节点caller的
        #     # in_e = find_e_node(e, node_list[caller])
        #     # in_e.message_pool.append(new_package)
        # else:
        #     # 数据包在进入网络的时候没有被检测到，没有被检测到说明什么，说明数据包的状态（这个是正常的包，而非恶意新增的包，但这个包会导致最终的结果检测失败）
        #     new_package.in_status = 0
        PACKAGE_ID += 1
        return True
    else:
        return None


def is_belongs_to_net(node, net):
    return node.type == net.type


# 产生流
def generate_send_stream(package):
    global STREAM_ID
    # 首先判断是否需要新建流
    for stream in SEND_STREAM_POOL:
        if (stream.caller_id == package.caller_id and stream.receiver_id == package.receiver_id):
            stream.package_list.append(package)
            package.stream_id = stream.id
            if (len(stream.package_list) == stream.size):
                # 如果流的数据包数量已经达到最大，则从发送流中移除，减少后续判断时间
                SEND_STREAM_POOL.remove(stream)
            return True
    #  如果已经发送的流里面没有对应的流的信息，则需要新建流
    new_stream = Stream(STREAM_ID, package.caller_id, package.receiver_id, STREAM_SIZE)
    new_stream.package_list.append(package)
    package.stream_id = new_stream.id
    SEND_STREAM_POOL.append(new_stream)
    STREAM_ID += 1


# 产生流
def generate_receive_stream(package):
    # 首先判断是否需要新建流
    for stream in RECEIVE_STREAM_POOL:
        if (stream.id == package.stream_id):
            stream.package_list.append(package)
            if (len(stream.package_list) == stream.size):
                COMPLETE_RECEIVE_STREAM_POOL.append(stream)
                RECEIVE_STREAM_POOL.remove(stream)
            return True
    new_stream = Stream(package.stream_id, package.caller_id, package.receiver_id, STREAM_SIZE)
    new_stream.package_list.append(package)
    RECEIVE_STREAM_POOL.append(new_stream)
    return True


# 完成消息的转发
def transmission_package(node):
    t_value = list()
    for N in node:
        t_value.append(N.transport_message())
    return t_value


# 完成消息的接收
def receiving_package(node_list, tran_results, wrongPathRate):
    global PACKAGE_LOSS_RATE
    k = 0
    while k < len(tran_results):
        if tran_results[k] == None:
            k += 1
            continue
        else:
            # 按照路由表转发的方式，让下一跳节点接收消息
            new_package = tran_results[k]
            # 加入自然丢包
            if random.random() < PACKAGE_LOSS_RATE:
                new_package.loss_status = 1
            elif random.random() < wrongPathRate:
                new_package.wrong_path_status = 1
            if new_package.receiver_id == node_list[k].mac:
                # if random.random() < out_detection_P:
                #     new_package.out_status = 1
                # else:
                #     # 说明出去的时候没有被检测到
                #     new_package.out_status = 0
                k += 1
                generate_receive_stream(new_package)
                continue
            if new_package.receiver_id in node_list[k].route_table:
                for N in node_list:
                    if N.mac == node_list[k].route_table[new_package.receiver_id]:  # 按照路由表的方式对数据包进行接收
                        N.receive_message(new_package)
            k += 1


def clear_net(node_list):
    global SEND_STREAM_POOL, RECEIVE_STREAM_POOL, COMPLETE_RECEIVE_STREAM_POOL
    for node in node_list:
        node.clear()
    SEND_STREAM_POOL = list()
    RECEIVE_STREAM_POOL = list()
    COMPLETE_RECEIVE_STREAM_POOL = list()


# 对于每个检测概率：考虑采取不同的产生错误数据包的概率（恶意程度）
# 衡量在不同的恶意程度下，检测成功率

def output_data(dataIndexList):
    global SLOT_NUM, ROUND_NUM
    now = datetime.now()
    s1 = now.strftime("%Y_%m%d_%H%M")
    workbook = xlsxwriter.Workbook('..\data_record\错误转发路径\自然丢包率\数据统计_lossRate_%s_%s.xlsx' % (PACKAGE_LOSS_RATE, s1),
                                   {'nan_inf_to_errors': True})
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


if __name__ == '__main__':
    # 考虑几件事情
    # 1、输入输出都有检测概率肯定是需要设置的；2、以流的形式进行传输，数据包还是逐个进行传输，只不过需要给数据包定义其属于哪个数据流
    # 3、数据流可以考虑为一个对象，也就是说每个数据包再进入网络的时候就需要对其进行标识，其属于哪个数据流，并且需要给数据包的状态进行表示
    # 4、考虑数据包有哪些状态：进入的时候被检测到，进入的时候被漏检，出去的时候被检测到，出去的时候被漏检，
    # 在中间转发的时候被丢包，恶意新增的数据包，被篡改路径的数据包
    # 代码逻辑
    G, SUBNET_LIST = manet_generator()
    node_list = list(G.nodes())
    in_detection_p = 1
    out_detection_p = 1
    malicious_p = [0.0001,0.001,0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1]
    # malicious_p = [0.001]
    dataIndexList = list()
    for mp in malicious_p:
        env = simpy.Environment()
        env.process(sim_run(env, node_list, mp))
        env.run()
        stream_type_green2green = 0
        stream_type_green2red = 0
        stream_type_red2green = 0
        stream_type_red2red = 0
        for stream in COMPLETE_RECEIVE_STREAM_POOL:
            only_nature_loss_package_num = 0;
            wrong_path_and_loss_package_num = 0;
            only_wrong_path_package_num = 0;
            no_wrong_path_no_loss_package_num = 0;
            for package in stream.package_list:
                if package.wrong_path_status == 1 and package.loss_status == 1:
                    wrong_path_and_loss_package_num += 1
                if package.wrong_path_status == -1 and package.loss_status == 1:
                    only_nature_loss_package_num += 1
                if package.wrong_path_status == 1 and package.loss_status == -1:
                    only_wrong_path_package_num += 1
                if package.new_add_status == -1 and package.loss_status == -1:
                    no_wrong_path_no_loss_package_num += 1
            if only_wrong_path_package_num > 0:
                stream_type_red2red += 1
                continue
            if only_nature_loss_package_num > 0 and wrong_path_and_loss_package_num == 0:
                stream_type_green2red += 1
                continue
            if only_nature_loss_package_num == 0 and wrong_path_and_loss_package_num == 0:
                stream_type_green2green += 1
                continue
            if only_nature_loss_package_num > 0 and wrong_path_and_loss_package_num > 0:
                stream_type_red2red += 1
        dataIndex = DataIndex(mp, stream_type_green2green, stream_type_green2red, stream_type_red2green,
                              stream_type_red2red, len(COMPLETE_RECEIVE_STREAM_POOL))
        # 计算那三个指标
        TP = dataIndex.red2red  # 真阳性的数量
        FP = dataIndex.green2red  # 假阳性
        FN = dataIndex.red2green  # 假阴性的数量
        TN = dataIndex.green2green  # 真阴性的数量
        if TP != 0:
            dataIndex.jaccard = TP / (TP + FP + FN)
            dataIndex.fm = math.sqrt((TP / (TP + FP)) * (TP / (TP + FN)))
            dataIndex.randIndex = (TP + TN) / (TP + FP + FN + TN)
        dataIndexList.append(dataIndex)
        clear_net(node_list)
    # 这里就可以调用数据统计函数了去写文件
    output_data(dataIndexList)
