import math
from typing import Tuple

import numpy
import pygame
import GLOBAL
from projectile import Projectile, Danmaku
from collision import collider_sprite


class Enemy:

    def __init__(self, pos):
        self.spawnx, self.spawny = self.spawn_pos = pos
        self.x, self.y = pos
        self.surface: pygame.Surface

        self.faction = "enemy"
        self.collider: pygame.sprite.Sprite | None = None
        self.collided = []
        self.health = 100  # OVERRIDE THIS IN YOUR ENEMY CLASS

        self.time = 0

    @property
    def pos(self):
        return numpy.array([self.x, self.y])

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


class TestEnemy(Enemy):
    danmaku = Danmaku("enemy")

    class test_bullet(Projectile):
        SPEED = 200
        IMAGE = pygame.Surface((10, 10))
        pygame.draw.circle(IMAGE, (0, 0, 255), IMAGE.get_rect().center, IMAGE.get_rect().width)

        def __init__(self, pos):
            self.pos = pos
            self.direction = numpy.arctan2(*(numpy.array(pos) - GLOBAL.PLAYER.collider.rect.center - [20, 20])[::-1]) + math.pi  # todo figure out where shit is fucking up to make me need this offset
            self.scalars = numpy.array([math.cos(self.direction), math.sin(self.direction)], dtype=float)
            self.image = TestEnemy.test_bullet.IMAGE
            super().__init__(numpy.array(pos) - numpy.array(self.image.get_size()) // 2, [10, 5])

        def update(self, dt):
            self.pos = (self.pos + (self.scalars * (dt * TestEnemy.test_bullet.SPEED)))

        @property
        def rect(self):
            return pygame.Rect(self.pos, self.size)

    def __init__(self, pos):
        super().__init__(pos)
        S = pygame.Surface((20, 20)).convert_alpha()
        S.fill((255, 255, 0, 255))
        self.surface = S

        self.bulletCD = 3
        self.bullet_CD_counter = self.bulletCD

        self.collider = collider_sprite(20)

    def update(self, dt):
        super(TestEnemy, self).update(dt)
        self.collider.rect = pygame.Rect(self.x, self.y, self.collider.size, self.collider.size)
        self.behavior(dt)

    def behavior(self, dt):
        # self.x = self.spawnx + 50 * math.sin(self.time * 3)
        self.bullet_CD_counter -= dt
        if self.bullet_CD_counter <= 0:
            self.bullet_CD_counter = self.bulletCD
            TestEnemy.danmaku.add(TestEnemy.test_bullet(self.collider.rect.center))
