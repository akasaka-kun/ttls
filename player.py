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
    surface = [(b := pygame.Surface((10, 10))).fill((255, 0, 0)), b][1]  # this is cursed and I love it
    collider = ("circle", 5)
    SPEED = 300

    @staticmethod
    def update_pos(pos, time, **kwargs) -> dict:
        return {"pos": kwargs["spawn_pos"] + (numpy.array([math.cos(kwargs["dir"]), math.sin(kwargs["dir"])], dtype=float) * (time*test_bullet.SPEED))}

    @staticmethod
    def new_bullet() -> dict:
        return {"damage": 20}


class Player(Renderable):

    BULLET_DELAY = .150

    def __init__(self, controller):
        GLOBAL.TO_RENDER.append(self)
        GLOBAL.TO_UPDATE.append(self)
        self.controller = controller
        self.faction = "player"

        self.v = numpy.zeros(2, dtype=float)
        self.x = 500
        self.y = 800

        self.danmaku = projectile.Danmaku(test_bullet, self.faction)
        self.bulletCD = 0

        S = pygame.Surface((20, 20)).convert_alpha()
        S.fill((255, 0, 0, 255))
        self.surface = S

    @property
    def pos(self):
        return numpy.array([self.x, self.y])

    def update(self, dt):
        self.v.fill(0)
        self.bulletCD = max(0, self.bulletCD-dt)
        for a in self.controller.actions:  # todo state detection for animation system
            match a:

                # move
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

                # shoot
                case "shootUp":
                    if self.bulletCD == 0:
                        self.bulletCD = Player.BULLET_DELAY
                        self.danmaku.add_bullet(self.pos, dir=1.5*math.pi, spawn_pos=self.pos)
                case "shootDown":
                    if self.bulletCD == 0:
                        self.bulletCD = Player.BULLET_DELAY
                        self.danmaku.add_bullet(self.pos, dir=.5*math.pi, spawn_pos=self.pos)
                case "shootLeft":
                    if self.bulletCD == 0:
                        self.bulletCD = Player.BULLET_DELAY
                        self.danmaku.add_bullet(self.pos, dir=math.pi, spawn_pos=self.pos)
                case "shootRight":
                    if self.bulletCD == 0:
                        self.bulletCD = Player.BULLET_DELAY
                        self.danmaku.add_bullet(self.pos, dir=0, spawn_pos=self.pos)

        self.x, self.y = [bind(i, bound_rect[0][n], bound_rect[1][n]) for n, i in enumerate((self.x, self.y) + self.v * dt)]
