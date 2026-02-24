import pygame
import pickle
import os
from .world import World
from .player import Player
from .entities import Enemy, Bullet


class Game:
    TILE = 32
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('迷你RPG原型')
        self.clock = pygame.time.Clock()
        self.world = World(25, 18)
        px, py = self.world.random_floor()
        self.player = Player(px, py)
        self.entities = []
        for _ in range(8):
            ex, ey = self.world.random_floor()
            if (ex, ey) != (self.player.x, self.player.y):
                self.entities.append(Enemy(ex, ey))
        # 地图上的掉落物（物品名, x, y, 数量）
        self.items_on_ground = []
        # 使用支持中文的字体
        self.font = pygame.font.SysFont('SimHei', 18)
        # 加载玩家图片
        self.player_img = pygame.image.load(os.path.join(os.path.dirname(__file__), 'image', 'player.png')).convert_alpha()
        self.message = ''
        self.running = True
        self.projectiles = []

    def save(self, path='savegame.dat'):
        data = {
            'world': self.world.tiles,
            'player': (self.player.x, self.player.y, self.player.hp, self.player.inventory),
            'entities': [(e.x, e.y, e.kind, e.hp) for e in self.entities]
        }
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        self.message = '已保存。'

    def load(self, path='savegame.dat'):
        if not os.path.exists(path):
            self.message = '未找到存档。'
            return
        with open(path, 'rb') as f:
            data = pickle.load(f)
        # restore basic state
        tiles = data.get('world')
        if tiles:
            self.world.tiles = tiles
        px, py, php, pinv = data.get('player', (self.player.x, self.player.y, self.player.hp, []))
        self.player.x, self.player.y = px, py
        self.player.hp = php
        self.player.inventory = pinv
        self.entities = [Enemy(x, y, kind) for x, y, kind, hp in data.get('entities', [])]
        for e, (_, _, _, hp) in zip(self.entities, data.get('entities', [])):
            e.hp = hp
        self.message = '已加载。'

    def handle_keys(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_s:
                    self.save()
                elif event.key == pygame.K_l:
                    self.load()
                elif event.key == pygame.K_i:
                    # 友好显示背包
                    if not self.player.inventory:
                        self.message = '背包为空'
                    else:
                        msg = '背包: '
                        msg += '，'.join([f'{k}x{v}' for k, v in self.player.inventory.items()])
                        self.message = msg
                elif event.key == pygame.K_u:
                    # 使用药水
                    if self.player.use_item('药水'):
                        self.player.hp = min(self.player.max_hp, self.player.hp + 10)
                        self.message = '你使用了药水，恢复10点生命。'
                    else:
                        self.message = '没有药水可用。'
                elif event.key == pygame.K_SPACE:
                    # shoot in facing direction
                    dx, dy = self.player.shoot_direction()
                    if dx == 0 and dy == 0:
                        self.message = '没有射击方向。'
                    else:
                        bx, by = self.player.x + dx, self.player.y + dy
                        if self.world.is_walkable(bx, by):
                            self.projectiles.append(Bullet(bx, by, dx, dy, self.player.atk))
                            self.message = '你开枪了。'
                        else:
                            self.message = '不能朝墙壁射击。'
                else:
                    self.try_move(event.key)

    def try_move(self, key):
        mapping = {
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_w: (0, -1),
            pygame.K_s: (0, 1),
            pygame.K_a: (-1, 0),
            pygame.K_d: (1, 0),
        }
        if key not in mapping:
            return
        dx, dy = mapping[key]
        # update facing even if move will be blocked
        self.player.facing = (dx, dy)
        tx, ty = self.player.x + dx, self.player.y + dy
        # check enemy at target
        target = None
        for e in self.entities:
            if e.x == tx and e.y == ty and e.is_alive():
                target = e
                break
        if target:
            # attack
            target.take_damage(self.player.atk)
            self.message = f'你攻击了{target.kind}，造成{self.player.atk}点伤害。'
            if not target.is_alive():
                self.message += ' 敌人死亡。'
                # 敌人死亡有概率掉落药水
                import random
                if random.random() < 0.5:
                    self.items_on_ground.append(('药水', target.x, target.y, 1))
        else:
            moved = self.player.move(dx, dy, self.world)
            if moved:
                # entities act
                for e in self.entities:
                    if e.is_alive():
                        # if adjacent to player, attack
                        if abs(e.x - self.player.x) + abs(e.y - self.player.y) == 1:
                            self.player.take_damage(e.atk)
                            self.message = f'敌人攻击你，造成{e.atk}点伤害！'
                        else:
                            e.act(self.player, self.world)

    def update_projectiles(self):
        # move projectiles, check collisions with entities and walls
        for b in self.projectiles[:]:
            nx = b.x + b.dx
            ny = b.y + b.dy
            # check entity collision
            hit = None
            for e in self.entities:
                if e.is_alive() and e.x == nx and e.y == ny:
                    hit = e
                    break
            if hit:
                hit.take_damage(b.dmg)
                self.message = f'子弹击中了{hit.kind}，造成{b.dmg}点伤害。'
                try:
                    self.projectiles.remove(b)
                except ValueError:
                    pass
                continue
            # check walls
            if not self.world.is_walkable(nx, ny):
                try:
                    self.projectiles.remove(b)
                except ValueError:
                    pass
                continue
            # move
            b.x, b.y = nx, ny

    def draw(self):
        self.screen.fill((10, 10, 10))
        for y in range(self.world.h):
            for x in range(self.world.w):
                rect = pygame.Rect(x*self.TILE, y*self.TILE, self.TILE, self.TILE)
                if self.world.tiles[y][x] == '#':
                    pygame.draw.rect(self.screen, (40, 40, 40), rect)
                else:
                    pygame.draw.rect(self.screen, (100, 100, 120), rect)
        # entities
        for e in self.entities:
            if e.is_alive():
                rect = pygame.Rect(e.x*self.TILE, e.y*self.TILE, self.TILE, self.TILE)
                pygame.draw.rect(self.screen, (180, 50, 50), rect)
        # 掉落物
        for name, x, y, count in self.items_on_ground:
            rect = pygame.Rect(x*self.TILE+8, y*self.TILE+8, self.TILE-16, self.TILE-16)
            pygame.draw.rect(self.screen, (80, 200, 255), rect)
            txt = self.font.render(name, True, (0,0,0))
            self.screen.blit(txt, (x*self.TILE+10, y*self.TILE+10))
        # projectiles
        for b in self.projectiles:
            rect = pygame.Rect(int(b.x*self.TILE + self.TILE*0.25), int(b.y*self.TILE + self.TILE*0.25), int(self.TILE*0.5), int(self.TILE*0.5))
            pygame.draw.rect(self.screen, (240, 220, 50), rect)
        # player
        prect = pygame.Rect(self.player.x*self.TILE, self.player.y*self.TILE, self.TILE, self.TILE)
        img = pygame.transform.scale(self.player_img, (self.TILE, self.TILE))
        self.screen.blit(img, prect)

        # HUD
        hp_surf = self.font.render(f'生命: {self.player.hp}/{self.player.max_hp}', True, (255,255,255))
        self.screen.blit(hp_surf, (self.world.w*self.TILE + 8, 8))
        msg_surf = self.font.render(self.message, True, (220,220,220))
        self.screen.blit(msg_surf, (8, self.world.h*self.TILE + 4))

    def run(self):
        # adjust screen to fit HUD area
        total_w = max(800, self.world.w*self.TILE + 200)
        total_h = max(600, self.world.h*self.TILE + 40)
        self.screen = pygame.display.set_mode((total_w, total_h))
        victory = False
        while self.running and self.player.is_alive() and not victory:
            self.handle_keys()
            self.update_projectiles()
            # 检查玩家是否在掉落物上，自动拾取
            for item in self.items_on_ground[:]:
                name, x, y, count = item
                if self.player.x == x and self.player.y == y:
                    self.player.add_item(name, count)
                    self.items_on_ground.remove(item)
                    self.message = f'你捡起了{name}x{count}'
            self.draw()
            pygame.display.flip()
            self.clock.tick(30)
            # 检查是否所有敌人都死亡
            if all(not e.is_alive() for e in self.entities):
                victory = True

        if victory:
            self.screen.fill((0,0,0))
            win1 = self.font.render('胜利！你消灭了所有敌人！', True, (255,220,80))
            win2 = self.font.render('恭喜通关！按任意键退出。', True, (255,255,255))
            self.screen.blit(win1, (40, 40))
            self.screen.blit(win2, (40, 100))
            pygame.display.flip()
            waiting = True
            while waiting:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        waiting = False
                    elif ev.type == pygame.KEYDOWN:
                        waiting = False
        elif not self.player.is_alive():
            self.screen.fill((0,0,0))
            go = self.font.render('你死了。按任意键退出。', True, (255,80,80))
            self.screen.blit(go, (20, 20))
            pygame.display.flip()
            waiting = True
            while waiting:
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        waiting = False
                    elif ev.type == pygame.KEYDOWN:
                        waiting = False
        pygame.quit()
