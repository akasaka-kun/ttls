import math
from typing import Tuple

import pygame
import GLOBAL


class Enemy:

    def __init__(self, pos):
        self.spawnx, self.spawny = self.spawn_pos = pos
        self.x, self.y = pos
        self.surface: pygame.Surface

        self.faction = "enemy"
        self.collider: Tuple[str, ...]
        self.collided = []
        self.health = 100  # OVERRIDE THIS IN YOUR ENEMY CLASS

        self.time = 0

    @property
    def pos(self):
        return self.x, self.y

    @classmethod
    def spawn(cls, pos):
        new_enemy: Enemy = cls(pos)
        GLOBAL.TO_UPDATE.append(new_enemy)
        if getattr(new_enemy, 'surface', None): GLOBAL.TO_RENDER.append(new_enemy)
        GLOBAL.ENEMIES.append(new_enemy)
        print(f'[spawned enemy] {new_enemy}')
        return new_enemy

    def update(self, dt):
        self.time += dt
        for i in range(len(self.collided)):
            self.handle_collision(self.collided.pop(i))

    def handle_collision(self, collided_with: dict):
        if collided_with.get("damage"):
            self.health -= collided_with["damage"]
            if self.health <= 0: print("DEAD")


class TestEnemy(Enemy):

    def __init__(self, pos):
        super().__init__(pos)
        S = pygame.Surface((20, 20)).convert_alpha()
        S.fill((255, 255, 0, 255))
        self.surface = S

        self.collider = ("circle", 10)

    def update(self, dt):
        super(TestEnemy, self).update(dt)
        self.x = self.spawnx + 50 * math.sin(self.time * 3)
