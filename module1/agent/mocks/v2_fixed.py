from collections import OrderedDict

class LRUCache:
    """
    Least Recently Used (LRU) Cache using collections.OrderedDict.
    Fixes O(1) performance and capacity zero boundary handling based on critique.
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if self.capacity <= 0:
            return -1
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if self.capacity <= 0:
            return
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

