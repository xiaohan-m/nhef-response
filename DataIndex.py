class DataIndex(object):
    def __init__(self, mp, green2green, green2red, red2green, red2red,size):
        self.mp = mp
        self.green2green = green2green
        self.green2red = green2red
        self.red2green = red2green
        self.red2red = red2red
        self.size = size
        self.jaccard = 0
        self.fm = 0
        self.randIndex = 0

    def __str__(self):
        return 'mp:%s  green2green:%s  green2red:%s  red2green:%s  red2red:%s' % (
            self.mp, self.green2green, self.green2red, self.red2green, self.red2red)

    __repr__ = __str__


if __name__ == '__main__':
    dataIndex = DataIndex()
    dataIndex.mp = 0.001
    dataIndex.green2green = 1
    dataIndex.green2red = 2
    dataIndex.red2green = 3
    dataIndex.red2red = 4
    print(dataIndex)
