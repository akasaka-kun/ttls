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
        self.collider: pygame.sprite.Sprite|None = None
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
        for i in GLOBAL.PROJECTILE_GROUPS:
            if i.faction != self.faction:
                collisions = pygame.sprite.spritecollide(self.collider, i, True, pygame.sprite.collide_circle)
                for projectile in collisions:
                    self.health -= projectile.damage
        if self.health <= 0:  # later : play death animations, drop stuff, this kinda shit
            GLOBAL.TO_UPDATE.remove(self)
            GLOBAL.TO_RENDER.remove(self)
            del self

    def handle_collision(self, collided_with: dict):
        if collided_with.get("damage"):
            self.health -= collided_with["damage"]
            if self.health <= 0: print("DEAD")


class collider_sprite(pygame.sprite.Sprite):
    def __init__(self, size):
        super().__init__()
        self.size = size
        self.rect = pygame.Rect([0, 0, size, size])


class TestEnemy(Enemy):

    def __init__(self, pos):
        super().__init__(pos)
        S = pygame.Surface((20, 20)).convert_alpha()
        S.fill((255, 255, 0, 255))
        self.surface = S

        self.collider = collider_sprite(20)

    def update(self, dt):
        super(TestEnemy, self).update(dt)
        self.collider.rect[0], self.collider.rect[1] = self.x, self.y
        self.x = self.spawnx + 50 * math.sin(self.time * 3)
