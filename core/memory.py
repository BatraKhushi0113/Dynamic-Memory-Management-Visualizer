class Memory:
    def __init__(self, size):
        self.size = size
        self.frames = [None] * size

    def load_page(self, index, page):
        self.frames[index] = page