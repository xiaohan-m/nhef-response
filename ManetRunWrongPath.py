# @Time     :2021/10/9 17:42
# @Author   :pc chen


"""
考虑错误转发路径
"""
from datetime import datetime
import random
import simpy
import xlsxwriter
from network.ManetTopology import manet_generator, find_net, find_e_subnet, find_e_node
from network.Package import Package

# global 变量
from network.Stream import Stream

PACKAGE_ID = 1  # 用来记录数据包的编号
TRAFFIC_LOAD = 0.5  # 系统强度(每个时隙产生正常数据包的概率)
SLOT_NUM = 20000

SEND_STREAM_POOL = list()
RECEIVE_STREAM_POOL = list()
COMPLETE_RECEIVE_STREAM_POOL = list()
STREAM_ID = 1
STREAM_SIZE = 5
PACKAGE_LOSS_RATE = 0.1


def sim_run(env, node_list, wrongPathRate):
    # 接下来是每个时隙都要干的事情
    global SLOT_NUM
    while True:
        if env.now % 10000 == 0:
            print('当前仿真间隙：', env.now)
        if env.now == SLOT_NUM:
            # print('当前仿真间隙：', env.now, "当前检测概率：", dp, "当前节点恶意程度:", mp)
            break
        generate_message(node_list)
        # 对每个节点判断自己的发送池中是否有消息需要转发
        # 完成消息传输
        tran_results = transmission_package(node_list)
        yield env.timeout(1)
        # 下一个时隙完成消息接收
        receiving_package(node_list, tran_results,wrongPathRate)


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
def receiving_package(node_list, tran_results,wrongPathRate):
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



def clear_net(node, SUBNET_LIST):
    for n in node:
        n.clear()
    for net in SUBNET_LIST:
        net.clear_event()


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
    # 考虑几件事情
    # 1、输入输出都有检测概率肯定是需要设置的；2、以流的形式进行传输，数据包还是逐个进行传输，只不过需要给数据包定义其属于哪个数据流
    # 3、数据流可以考虑为一个对象，也就是说每个数据包再进入网络的时候就需要对其进行标识，其属于哪个数据流，并且需要给数据包的状态进行表示
    # 4、考虑数据包有哪些状态：进入的时候被检测到，进入的时候被漏检，出去的时候被检测到，出去的时候被漏检，
    # 在中间转发的时候被丢包，恶意新增的数据包，被篡改路径的数据包
    # 代码逻辑
    G, SUBNET_LIST = manet_generator()
    node = list(G.nodes())
    in_detection_p = 1
    out_detection_p = 1
    env = simpy.Environment()
    wrongPathRate = 0.001
    env.process(sim_run(env, node, wrongPathRate))
    env.run()
    for stream in COMPLETE_RECEIVE_STREAM_POOL:
        # for package in stream.package_list:
        #     if package.wrong_path_status == 1 and package.loss_status == 1:
        if(len(stream.package_list)<5):
            print(len(stream.package_list))
