class Stream(object):
    def __init__(self, id, caller_id, receiver_id, size):
        self.id = id
        self.caller_id = caller_id
        self.receiver_id = receiver_id
        self.size = size
        self.package_list = list()

    def __str__(self):
        return 'Stream:\tid:%s\tpath:%s --> %s\tpackage_list:%s' % (self.id, self.caller_id, self.receiver_id, self.package_list)

    __repr__ = __str__



if __name__ == '__main__':
    s = Stream(1,0,5,10)
    s.package_list.append(1)
    s.package_list.append(2)
    s.package_list.append(3)
    print(s)
