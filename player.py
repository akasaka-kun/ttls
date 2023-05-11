import math

import numpy
import pygame

import projectile
from misc import bind
from config import bound_rect

import GLOBAL
from render import Renderable

# noinspection SpellCheckingInspection
V = 200


class test_bullet(projectile.projectile):
    surface = [(b := pygame.Surface((10, 10))).fill((255, 0, 0)), b][1]  # this is cursed and i love it

    @staticmethod
    def update_pos(pos, time, **kwargs) -> dict:
        return {"pos": kwargs["spawn_pos"] + (numpy.array([math.cos(kwargs["dir"]), math.sin(kwargs["dir"])], dtype=float) * (time*200))}


class Player(Renderable):

    def __init__(self, controller):
        GLOBAL.TO_RENDER.append(self)
        GLOBAL.TO_UPDATE.append(self)
        self.controller = controller
        self.faction = "player"

        self.v = numpy.zeros(2, dtype=float)
        self.x = 500
        self.y = 800

        self.danmaku = projectile.Danmaku(test_bullet, self.faction)

        S = pygame.Surface((20, 20)).convert_alpha()
        S.fill((255, 0, 0, 255))
        self.surface = S

    @property
    def pos(self):
        return numpy.array([self.x, self.y])

    def update(self, dt):
        self.v.fill(0)
        for a in self.controller.actions:  # todo state detection for animation system
            match a:
                case "up":
                    self.v[1] = -V
                case "left":
                    self.v[0] = -V
                case "down":
                    self.v[1] = V
                case "right":
                    self.v[0] = V
                case "focus":
                    self.v = self.v / 1.5
                case "shoot":
                    self.danmaku.add_bullet(self.pos, dir=1.5*math.pi, spawn_pos=self.pos)
        self.x, self.y = [bind(i, bound_rect[0][n], bound_rect[1][n]) for n, i in enumerate((self.x, self.y) + self.v * dt)]
