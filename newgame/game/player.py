class Player:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.hp = 30
        self.max_hp = 30
        self.atk = 6
        self.defense = 1
        # 背包为物品名到数量的字典
        self.inventory = {}
        # facing direction used for shooting (dx, dy)
        self.facing = (1, 0)

    def move(self, dx, dy, world):
        nx, ny = self.x + dx, self.y + dy
        if world.is_walkable(nx, ny):
            self.x, self.y = nx, ny
            # update facing when moving
            if dx != 0 or dy != 0:
                self.facing = (dx, dy)
            return True
        return False

    def shoot_direction(self):
        """Return current facing direction as (dx, dy)."""
        return self.facing

    def take_damage(self, amt):
        self.hp -= max(1, amt - self.defense)

    def is_alive(self):
        return self.hp > 0

    def add_item(self, name, count=1):
        if name in self.inventory:
            self.inventory[name] += count
        else:
            self.inventory[name] = count

    def use_item(self, name):
        if self.inventory.get(name, 0) > 0:
            self.inventory[name] -= 1
            if self.inventory[name] <= 0:
                del self.inventory[name]
            return True
        return False
