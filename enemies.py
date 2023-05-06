import math

import pygame
import GLOBAL


class Enemy:

    def __init__(self, pos):
        self.spawnx, self.spawny = self.spawn_pos = pos
        self.x, self.y = self.pos = pos
        self.surface: pygame.Surface

        self.time = 0

    @classmethod
    def spawn(cls, pos):
        new_enemy: Enemy = cls(pos)
        GLOBAL.TO_UPDATE.append(new_enemy)
        if getattr(new_enemy, 'surface', None): GLOBAL.TO_RENDER.append(new_enemy)
        print(f'[spawned enemy] {new_enemy}')
        return new_enemy

    def update(self, dt):
        self.time += dt


class TestEnemy(Enemy):

    def __init__(self, pos):
        super().__init__(pos)
        S = pygame.Surface((20, 20)).convert_alpha()
        S.fill((255, 255, 0, 255))
        self.surface = S

    def update(self, dt):
        super(TestEnemy, self).update(dt)
        self.x = self.spawnx + 50 * math.sin(self.time * 3)