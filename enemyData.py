import math
from typing import Generator, Callable

import numpy
import pygame
import beziers.cubicbezier as Curve
from weakref import ref

import GLOBAL
import config
import misc
import projectile
from collision import collider_sprite
from enemies import Enemy
from projectile import Projectile, Danmaku
from textures.atlas import Atlas


class TestEnemy(Enemy):
    danmaku = Danmaku("enemy")

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

        class Preset:
            left = ["moveLeft", -150, [Curve.Point(1000, 0), Curve.Point(850, 200), Curve.Point(700, 200)], [Curve.Point(250, 200), Curve.Point(0, 200), Curve.Point(0, 300)]]
            right = ["moveRight", 150, [Curve.Point(0, 0), Curve.Point(150, 200), Curve.Point(300, 200)], [Curve.Point(750, 200), Curve.Point(1000, 200), Curve.Point(1000, 300)]]
            ease_down = [Curve.Point(pos[0], 0), Curve.Point(pos[0], 250), Curve.Point(pos[0], 350)]
            forward = ["U-turn", 0, ease_down, ease_down[::-1]]

        self.Preset = Preset

        self.texture_atlas = Atlas('textures/TestEnemy.png', (22, 20),
                                   [i + str(j) for j in range(5) for i in ["moveRight", "moveLeft", "U-turn"]],
                                   [(0, 0, -1, 0)] * 3 * 5)
        self.animation_state = ""
        self.animation_frame_duration = 0.2
        self.animation_frame_count = 5

        self.health = 30

        if preset is None:
            preset = self.Preset.left
        else:
            preset = getattr(self.Preset, preset)
        self.behavior_ = self.behavior(*preset)

        self.collider = collider_sprite(20)

    def update(self, dt: float):
        super(TestEnemy, self).update(dt)
        self.collider.rect = pygame.Rect(self.x, self.y, self.collider.size, self.collider.size)

    def behavior(self, animation_side, V, path_in, path_out):

        self.animation_state = animation_side
        yield self.path(path_in, duration=1)
        self.danmaku.add(self.test_bullet(self.collider.rect.center))

        for i in range(3):
            yield self.move([V, 0], duration=1)
            self.danmaku.add(self.test_bullet(self.collider.rect.center))

        yield self.path(path_out, duration=1)
        self.danmaku.add(self.test_bullet(self.collider.rect.center))


class Yukari(Enemy):
    danmaku = Danmaku("enemy")  # todo own Danmaku

    class Laser(Projectile):
        def __init__(self, pos, end_anchor, color, thickness):
            self.pos = pos
            self.start = pos
            self.end_anchor = end_anchor  # should be a reference?
            self.end = end_anchor.pos
            self.color = color
            self.thickness = thickness
            self.image = self.texture()
            super().__init__(numpy.array(pos) - numpy.array(self.image.get_size()) // 2, [1, 1])

        def update(self, dt):
            self.end = getattr(self.end_anchor, "pos")
            self.pos = numpy.array((min(self.end[0], self.start[0]), min(self.end[1], self.start[1]))) - self.thickness
            self.image = self.texture()

        def fixate_end(self):
            self.end_anchor = projectile.Anchor(getattr(self.end_anchor, "pos"))

        def texture(self):
            print(self.color)
            topleft = numpy.array((min(self.end[0], self.start[0]), min(self.end[1], self.start[1]))) - self.thickness
            bottomright = numpy.array((max(self.end[0], self.start[0]), max(self.end[1], self.start[1]))) + self.thickness
            surf = pygame.Surface(bottomright-topleft, flags=pygame.SRCALPHA)
            pygame.draw.circle(surf, self.color, self.start-topleft, self.thickness//2)
            pygame.draw.circle(surf, self.color, self.end-topleft, self.thickness//2)
            misc.line(surf, self.color, self.start-topleft, self.end-topleft, width=self.thickness)
            return surf

        @property
        def rect(self):
            return pygame.Rect(self.pos, self.size)

    def __init__(self, pos, preset=None):
        super().__init__(pos)

        self.texture_atlas = Atlas('textures/TestEnemy.png', (22, 20),
                                   [i + str(j) for j in range(5) for i in ["moveRight", "moveLeft", "U-turn"]],
                                   [(0, 0, -1, 0)] * 3 * 5)
        self.animation_state = ""
        self.animation_frame_duration = 0.2
        self.animation_frame_count = 5

        self.health = 30

        self.behavior_ = self.behavior()

        self.collider = collider_sprite(20)

    def update(self, dt: float):
        super(self.__class__, self).update(dt)
        self.collider.rect = pygame.Rect(self.x, self.y, self.collider.size, self.collider.size)

    def behavior(self):

        # pattern 1
        center = GLOBAL.PLAYER.collider.rect.center - numpy.asarray(self.collider.size) // 2
        size = min(900 - center[0], 900 - center[1]) + 60
        self.animation_state = "U-turn"
        self.x, self.y = center[0], center[1] - size

        self.danmaku.add((laser := self.Laser(self.pos.copy(), self, (255, 0, 0), 10)))
        yield self.path([Curve.Point(center[0], center[1] - size), Curve.Point(center[0] + size, center[1])], duration=.6, easing=misc.easeInOutSine)
        laser.fixate_end()

        self.danmaku.add((laser := self.Laser(self.pos.copy(), self, (255, 0, 0), 10)))
        yield self.path([Curve.Point(center[0] + size, center[1]), Curve.Point(center[0], center[1] + size)], duration=.6, easing=misc.easeInOutSine)
        laser.fixate_end()

        self.danmaku.add((laser := self.Laser(self.pos.copy(), self, (255, 0, 0), 10)))
        yield self.path([Curve.Point(center[0], center[1] + size), Curve.Point(center[0] - size, center[1])], duration=.6, easing=misc.easeInOutSine)
        laser.fixate_end()

        self.danmaku.add((laser := self.Laser(self.pos.copy(), self, (255, 0, 0), 10)))
        yield self.path([Curve.Point(center[0] - size, center[1]), Curve.Point(center[0], center[1] - size)], duration=.6, easing=misc.easeInOutSine)
        laser.fixate_end()
