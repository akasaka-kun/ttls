import math
from typing import Generator, Callable

import numpy
import pygame
import beziers.cubicbezier as Curve

import GLOBAL
from collision import collider_sprite
from enemies import Enemy
from projectile import Projectile, Danmaku
from textures.atlas import Atlas


class TestEnemy(Enemy):
    danmaku = Danmaku("enemy")

    class Preset:
        left = ["moveLeft", -150, [Curve.Point(1000, 0), Curve.Point(850, 200), Curve.Point(700, 200)], [Curve.Point(250, 200), Curve.Point(0, 200), Curve.Point(0, 300)]]
        right = ["moveRight", 150, [Curve.Point(0, 0), Curve.Point(150, 200), Curve.Point(300, 200)], [Curve.Point(750, 200), Curve.Point(1000, 200), Curve.Point(1000, 300)]]

    class test_bullet(Projectile):
        SPEED = 200
        IMAGE = pygame.Surface((10, 10))
        pygame.draw.circle(IMAGE, (0, 0, 255), IMAGE.get_rect().center, IMAGE.get_rect().width)

        def __init__(self, pos):
            self.pos = pos
            self.direction = numpy.arctan2(*(numpy.array(pos) - GLOBAL.PLAYER.collider.rect.center)[::-1]) + math.pi
            self.scalars = numpy.array([math.cos(self.direction), math.sin(self.direction)], dtype=float)
            self.image = TestEnemy.test_bullet.IMAGE
            super().__init__(numpy.array(pos) - numpy.array(self.image.get_size()) // 2, [10, 5])

        def update(self, dt):
            self.pos = (self.pos + (self.scalars * (dt * TestEnemy.test_bullet.SPEED)))

        @property
        def rect(self):
            return pygame.Rect(self.pos, self.size)

    def __init__(self, pos, preset=None):
        super().__init__(pos)
        self.texture_atlas = Atlas('textures/TestEnemy.png', (22, 20),
                                   [i + str(j) for j in range(5) for i in ["moveRight", "moveLeft"]],
                                   [(0, 0, -1, 0)] * 2 * 5)
        self.animation_state = ""
        self.animation_frame_duration = 0.2
        self.animation_frame_count = 5

        self.health = 30

        if preset is None: preset = self.Preset.left
        self.behavior_ = self.behavior(*preset)

        self.collider = collider_sprite(20)

    def update(self, dt: float):
        super(TestEnemy, self).update(dt)
        self.collider.rect = pygame.Rect(self.x, self.y, self.collider.size, self.collider.size)

    def behavior(self, animation_side, V, path_in, path_out):

        self.animation_state = animation_side
        yield self.path(path_in, duration=1)
        self.danmaku.add(self.test_bullet(self.collider.rect.center))

        yield self.move([V, 0], duration=3)
        self.danmaku.add(self.test_bullet(self.collider.rect.center))

        yield self.path(path_out, duration=1)
        self.danmaku.add(self.test_bullet(self.collider.rect.center))
