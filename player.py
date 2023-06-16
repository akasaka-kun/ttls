import math

import numpy
import pygame

import animation_manager
import projectile
from misc import bind
from config import bound_rect

import GLOBAL
from render import Renderable
from textures.atlas import Atlas

# noinspection SpellCheckingInspection
V = 200


class test_bullet(projectile.projectile):
    surface = [(b := pygame.Surface((10, 10))).fill((255, 0, 0)), b][1]  # this is cursed and I love it
    SPEED = 300

    @staticmethod
    def update_pos(pos, time, **kwargs) -> dict:
        return {"pos": kwargs["spawn_pos"] + (numpy.array([math.cos(kwargs["dir"]), math.sin(kwargs["dir"])], dtype=float) * (time * test_bullet.SPEED))}


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

        # todo change this for a @property that returns the right animation frame
        S = pygame.Surface((20, 20)).convert_alpha()
        S.fill((255, 0, 0, 255))
        self.default_surface = S

        self.asm = animation_manager.state_manager({
            frozenset(("moveUp",)): ("moveUp", 1),
            frozenset(("moveDown",)): ("moveDown", 1),
            frozenset(("moveLeft",)): ("moveLeft", 1),
            frozenset(("moveRight",)): ("moveRight", 1),

            frozenset(("moveUp", "moveLeft")): ("moveUpLeft", 2),
            frozenset(("moveUp", "moveRight")): ("moveUpRight", 2),
            frozenset(("moveDown", "moveLeft")): ("moveDownLeft", 2),
            frozenset(("moveDown", "moveRight")): ("moveDownRight", 2),

            frozenset(("focus",)): ("Focus", 3)
        })
        self.texture_atlas = Atlas('textures/character.png', (22, 21),
                                   ["moveRight", "moveDown", "moveLeft", "moveUp", "moveUpRight", "moveDownRight", "moveDownLeft", "moveUpLeft", "Focus"],
                                   [(0, 0, -1, -1)] * 9)
        self._actions = []

    @property
    def pos(self):
        return numpy.array([self.x, self.y])

    @property
    def surface(self):
        return self.texture_atlas.get(self.asm.get_state(self._actions), self.default_surface)

    def update(self, dt):
        self._actions = []
        self.v.fill(0)
        self.bulletCD = max(0, self.bulletCD - dt)
        for a in self.controller.actions:  # todo list all concurrent actions
            match a:

                # move
                case "up":
                    self.v[1] = -V
                    self._actions.append("moveUp")
                case "left":
                    self.v[0] = -V
                    self._actions.append("moveLeft")
                case "down":
                    self.v[1] = V
                    self._actions.append("moveDown")
                case "right":
                    self.v[0] = V
                    self._actions.append("moveRight")

                # shoot
                case "shootUp":
                    if self.bulletCD == 0:
                        self.bulletCD = Player.BULLET_DELAY
                        self.danmaku.add_bullet(self.pos, dir=1.5 * math.pi, spawn_pos=self.pos)
                case "shootDown":
                    if self.bulletCD == 0:
                        self.bulletCD = Player.BULLET_DELAY
                        self.danmaku.add_bullet(self.pos, dir=.5 * math.pi, spawn_pos=self.pos)
                case "shootLeft":
                    if self.bulletCD == 0:
                        self.bulletCD = Player.BULLET_DELAY
                        self.danmaku.add_bullet(self.pos, dir=math.pi, spawn_pos=self.pos)
                case "shootRight":
                    if self.bulletCD == 0:
                        self.bulletCD = Player.BULLET_DELAY
                        self.danmaku.add_bullet(self.pos, dir=0, spawn_pos=self.pos)
        if "focus" in self.controller.actions:
            self.v /= 1.5
            self._actions.append("focus")

        self.x, self.y = [bind(i, bound_rect[0][n], bound_rect[1][n]) for n, i in enumerate((self.x, self.y) + self.v * dt)]
