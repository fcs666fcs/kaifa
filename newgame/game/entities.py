import random


class Enemy:
    def __init__(self, x, y, kind='goblin'):
        self.x = x
        self.y = y
        self.kind = kind
        self.hp = 10
        self.atk = 4

    def act(self, player, world):
        # simple AI: move towards player if nearby, otherwise wander
        dx = player.x - self.x
        dy = player.y - self.y
        dist = abs(dx) + abs(dy)
        if dist <= 6:
            step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
            step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
            # try x then y
            if world.is_walkable(self.x + step_x, self.y):
                self.x += step_x
            elif world.is_walkable(self.x, self.y + step_y):
                self.y += step_y
        else:
            if random.random() < 0.6:
                d = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
                if world.is_walkable(self.x + d[0], self.y + d[1]):
                    self.x += d[0]
                    self.y += d[1]

    def take_damage(self, amt):
        self.hp -= amt

    def is_alive(self):
        return self.hp > 0


class Bullet:
    def __init__(self, x, y, dx, dy, dmg=6, owner='player'):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.dmg = dmg
        self.owner = owner
        self.alive = True

    def step(self, world):
        nx = self.x + self.dx
        ny = self.y + self.dy
        # if next tile is walkable, move there, else die
        if world.is_walkable(nx, ny):
            self.x, self.y = nx, ny
            return True
        else:
            self.alive = False
            return False
