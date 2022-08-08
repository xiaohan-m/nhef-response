"""
    @Time     :2021/11/17 11:02
    @Author   :pc chen
    @Describe :
"""


class Event_monitor(object):
    def __init__(self, first_hop, next_hop):
        self.first_hop = first_hop
        self.next_hop = next_hop
        self.message_pool = list()

    def __str__(self):
        return '(%s,%s):%s' % (self.first_hop, self.next_hop, self.message_pool)

    __repr__ = __str__

    def clear_e(self):
        self.message_pool = list()


if __name__ == '__main__':
    e = Event_monitor(1, 2)
    e.message_pool.append(3)
    print(e)
