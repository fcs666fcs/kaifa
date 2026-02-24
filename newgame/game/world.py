import random


class World:
    def __init__(self, w=25, h=18, floor_ratio=0.40):
        self.w = w
        self.h = h
        self.tiles = [['#' for _ in range(w)] for _ in range(h)]
        self.generate(floor_ratio)

    def generate(self, floor_ratio=0.40):
        # Drunkard walk / random walk dungeon
        max_steps = int(self.w * self.h * floor_ratio)
        x, y = self.w // 2, self.h // 2
        self.tiles[y][x] = '.'
        for _ in range(max_steps):
            dir = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            nx, ny = x + dir[0], y + dir[1]
            if 1 <= nx < self.w-1 and 1 <= ny < self.h-1:
                x, y = nx, ny
                self.tiles[y][x] = '.'

    def is_walkable(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.tiles[y][x] == '.'
        return False

    def random_floor(self):
        import random
        empties = [(x, y) for y in range(self.h) for x in range(self.w) if self.tiles[y][x] == '.']
        return random.choice(empties) if empties else (self.w//2, self.h//2)
