import math
import numpy
import pygame
import beziers.cubicbezier as Curve
from typing import Generator, Callable

import GLOBAL
from projectile import Projectile, Danmaku
from collision import collider_sprite
from textures.atlas import Atlas


class Enemy:

    def __init__(self, pos, *args):
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
    def spawn(cls, pos, *args):
        new_enemy: Enemy = cls(pos, *args)
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
            self.kill()

    def kill(self):
        GLOBAL.TO_UPDATE.remove(self)
        GLOBAL.TO_RENDER.remove(self)
        del self

    def move(self, vec=None, pos=None):
        assert (vec is not None) != (pos is not None), "Provide either vec or pos but not both."
        if vec is not None:
            self.x, self.y = self.pos + vec
        elif pos is not None:
            self.x, self.y = pos

    def path(self, curvePoints, duration):
        t = 0
        curve = Curve.QuadraticBezier(*curvePoints)
        while t <= 1:
            dt = yield
            t += dt / duration
            pat = curve.pointAtTime(t).rounded()
            self.move(pos=[pat.x, pat.y])
