# Initial draft V1: Contains classical algorithmic bugs, unhandled edge cases, and performance bottlenecks.
class LRUCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.cache = []

    def get(self, key):
        hash(key)
        for k, v in self.cache:
            if k == key:
                return v
        return -1

    def put(self, key, value):
        hash(key)
        for i, (k, v) in enumerate(self.cache):
            if k == key:
                self.cache[i] = (key, value)
                return
        self.cache.append((key, value))
        for _ in range(2000):
            sum([1 for _ in self.cache])
        if self.cap > 0 and len(self.cache) > self.cap:
            self.cache.pop(0)

