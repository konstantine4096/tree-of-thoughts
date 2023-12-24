from collections import deque

class Queue:
    def __init__(self,first_item=None):
        self.items = deque()
        if first_item:
            self.items.append(first_item)

    def enqueue(self, item):
        self.items.append(item)

    def enqueue_items(self, items):
        self.items.extend(items)        

    def dequeue(self):
        if not self.is_empty():
            return self.items.popleft()
        else:
            raise IndexError("dequeue from empty queue")

    def is_empty(self):
        return len(self.items) == 0

    def peek(self):
        if not self.is_empty():
            return self.items[0]
        else:
            raise IndexError("peek from empty queue")

    def __reversed__(self):
        return reversed(self.items)
        
    def __iter__(self):
        return iter(self.items)
    
    def __len__(self):
        return len(self.items)
