class CItemList(list):
    def __init__(self, parent = None):
        self.parent = parent
    def add(self, item):
        item.list = self
        self.append(item)
        return self[-1]
    def delete(self, index):
        self.remove(self[index])
    def get(self, index):
        return self[index]
    def set(self, index):
        return self[index]
    def count(self):
        return len(self)
    def first(self):
        return self[0]
    def last(self):
        return self[self.count()-1]
    def indexOf(item):
        for index, item in enumerate(self):
            if self.get(index) == item:
                return index
        return -1

