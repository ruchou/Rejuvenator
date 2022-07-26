import collections


class LRU:
    def __init__(self, size=10):
        self.size = size
        self.lru_cache = collections.OrderedDict()

    def get(self, key):
        if key not in self.lru_cache:
            return -1
        else:
            self.lru_cache.move_to_end(key)
            return self.lru_cache[key]

    def put(self, key, value):
        self.lru_cache[key] = value
        self.lru_cache.move_to_end(key)

        if len(self.lru_cache) > self.size:
            self.lru_cache.popitem(last=False)

    def show_entries(self):
        print(self.lru_cache)


if __name__ == '__main__':
    cache = LRU(size=3)

    cache.put("1", "1")
    cache.put("2", "2")
    cache.put("3", "3")

    cache.get("1")
    cache.get("3")

    cache.put("4", "4")  # This will replace 2
    cache.show_entries()  # shows 1,3,4
    cache.put("5", "5")  # This will replace 1
    cache.show_entries()  # shows 3,4,5
