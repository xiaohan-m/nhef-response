"""
    @Time     :2021/9/26 16:03
    @Author   :pc chen
    @Describe :定义数据包结构,以及产生数据包的方法（根据不同的强度进行数据包的产生）
"""


class Package:
    def __init__(self, id, caller_id, receiver_id):
        self.caller_id = caller_id
        self.receiver_id = receiver_id
        self.id = id  # 数据包编号

        self.stream_id = -1
        self.in_status = -1
        self.out_status = -1
        self.loss_status = -1
        self.new_add_status = -1
        self.wrong_path_status = -1

        self.ledger = list()  # 账本：存放转发节点身份信息
        self.timestamp = list()
        self.flag = True

    def __str__(self):
        return 'id:%s' % self.id + '\tcaller_id:%s' % self.caller_id+'\treceiver_id:%s'%self.receiver_id + '\tstream_id:%s' % self.stream_id + '\tloss_status:%s' % self.loss_status + '\twrong_path_status:%s' % self.wrong_path_status + '\tnew_add_status:%s' % self.new_add_status
        # return 'id:%s' % self._id + '\tsend_node:%s' % self._head[0] + '\treceiver_node:%s' % self._head[
        #     1]+'\tflag:%s' % self.flag

    __repr__ = __str__



if __name__ == '__main__':
    p = Package(id=5, caller_id=2, receiver_id=8)
    p.message = "测试"
    p.ledger = [1, 2, 3, 4, 5]
    print(p)

