import math

import numpy
import pygame
import GLOBAL
from projectile import Projectile, Danmaku
from collision import collider_sprite
from textures.atlas import Atlas


class Enemy:

    def __init__(self, pos):
        self.spawnx, self.spawny = self.spawn_pos = pos
        self.x, self.y = pos
        self.animation_state = ""
        self.animation_frame_duration = 0.05
        self.animation_frame_count = 1

        self.faction = "enemy"
        self.collider: pygame.sprite.Sprite | None = None
        self.collided = []
        self.health = 100  # OVERRIDE THIS IN YOUR ENEMY CLASS

        self.texture_atlas: Atlas | None = None

        self.time = 0

    @property
    def surface(self):
        frame_number = str(int(self.time // self.animation_frame_duration % self.animation_frame_count))
        return pygame.transform.scale2x(self.texture_atlas.get(self.animation_state + frame_number, pygame.Surface((0, 0))))

    @property
    def pos(self):
        return numpy.array([self.x, self.y])

    @classmethod
    def spawn(cls, pos):
        new_enemy: Enemy = cls(pos)
        GLOBAL.TO_UPDATE.append(new_enemy)
        GLOBAL.TO_RENDER.append(new_enemy)
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

    def move(self, vec):
        self.x, self.y = self.pos + vec


# botched together enemy, would be cool to have more of its code back in the Enemy class
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
        self.texture_atlas = Atlas('textures/TestEnemy.png', (22, 20),
                                   [i + str(j) for j in range(5) for i in ["moveRight", "moveLeft"]],
                                   [(0, 0, -1, 0)] * 2 * 5)
        self.animation_state = ""
        self.animation_frame_duration = 0.2
        self.animation_frame_count = 5

        self.behavior_ = self.behavior()

        self.collider = collider_sprite(20)
        self.current_action = None

    def update(self, dt: float):
        super(TestEnemy, self).update(dt)
        self.collider.rect = pygame.Rect(self.x, self.y, self.collider.size, self.collider.size)
        if self.current_action is None or self.current_action[1] == 0:
            self.current_action = list(next(self.behavior_))
            print(self.current_action)
        action_time: float = min(dt, self.current_action[1])
        self.current_action[0](action_time)
        self.current_action[1] -= action_time

    def behavior(self):
        while True:
            self.animation_state = "moveRight"
            yield (lambda dt: self.move([100 * dt, 0])), 1
            self.danmaku.add(self.test_bullet(self.collider.rect.center))

            self.animation_state = "moveLeft"
            yield (lambda dt: self.move([-100 * dt, 0])), 1
            self.danmaku.add(self.test_bullet(self.collider.rect.center))
