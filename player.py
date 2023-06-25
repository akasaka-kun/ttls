import math

import numpy
import pygame

import projectile
from misc import bind
from config import bound_rect

import GLOBAL
from render import Renderable
from textures.atlas import Atlas

# noinspection SpellCheckingInspection
V = 400


class test_bullet(projectile.projectile):
    SPEED = 2000
    (IMAGE := pygame.Surface((3, 10))).fill((255, 0, 0))

    def __init__(self, pos, direction):
        self.direction = direction
        self.scalars = numpy.array([math.cos(self.direction), math.sin(self.direction)], dtype=float)
        self.image = pygame.transform.rotate(test_bullet.IMAGE, direction * (180 / math.pi) + 90)
        self.damage = 15
        super().__init__(numpy.array(pos) - numpy.array(self.image.get_size()) // 2, [10, 5])

    def update(self, dt):
        self.rect = pygame.Rect([*(self.rect.topleft + (self.scalars * (dt * test_bullet.SPEED))), *self.size])


class Player(Renderable):
    BULLET_DELAY = .050

    ANIMATION_FRAME_DURATION = 8
    ANIMATION_STATES = {
        frozenset(("idle",)): ("idle", 0),
        frozenset(("moveUp",)): ("moveUp", 1),
        frozenset(("moveDown",)): ("moveDown", 1),
        frozenset(("moveLeft",)): ("moveLeft", 1),
        frozenset(("moveRight",)): ("moveRight", 1),

        frozenset(("moveUp", "moveLeft")): ("moveUpLeft", 2),
        frozenset(("moveUp", "moveRight")): ("moveUpRight", 2),
        frozenset(("moveDown", "moveLeft")): ("moveDownLeft", 2),
        frozenset(("moveDown", "moveRight")): ("moveDownRight", 2),

        frozenset(("focus",)): ("Focus", 10)
    }

    def __init__(self, controller):
        GLOBAL.TO_RENDER.append(self)
        GLOBAL.TO_UPDATE.append(self)
        self.controller = controller
        self.faction = "player"

        self.v = numpy.zeros(2, dtype=float)
        self.x = 500
        self.y = 800

        self.danmaku = projectile.Danmaku(self.faction)
        self.bullet_CD_Timer = 0

        self.width, self.height = 40, 40
        S = pygame.Surface((self.width / 2, self.height / 2)).convert_alpha()
        S.fill((255, 0, 0, 255))
        self.default_surface = S

        self.animation_state = ("", 1)
        self.texture_atlas = Atlas('textures/character.png', (22, 20),
                                   [i + str(j) for j in range(5) for i in ["moveRight", "moveDown", "moveLeft", "moveUp", "moveUpRight", "moveDownRight", "moveDownLeft", "moveUpLeft", "Focus", "idle"]],
                                   [(0, 0, -1, 0)] * 10 * 5)
        self._actions = []

    @property
    def pos(self):
        return numpy.array([self.x, self.y])

    @property
    def surface(self):

        current = ("idle", 0)
        for c, s in Player.ANIMATION_STATES.items():
            if all(i in self._actions for i in c):
                prio = s[1] + sum(n for n, a in enumerate(self._actions) if a in c)
                if current[1] < prio:
                    current = s[0], prio
        self.animation_state = current[0], 0 if current[0] != self.animation_state[0] else (self.animation_state[1] + 1)
        print(self.animation_state)
        frame_number = str(self.animation_state[1] // Player.ANIMATION_FRAME_DURATION % 5)
        return pygame.transform.scale2x(self.texture_atlas.get(current[0] + frame_number, self.texture_atlas.get("idle" + frame_number, self.default_surface)))

    def update(self, dt):
        self._actions = []
        self.v.fill(0)
        self.bullet_CD_Timer = max(0, self.bullet_CD_Timer - dt)
        for a in self.controller.actions:
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
                    if self.bullet_CD_Timer == 0:
                        self.bullet_CD_Timer = Player.BULLET_DELAY
                        self.danmaku.add(test_bullet(self.pos + [self.width / 2 - 6, self.height], direction=1.5 * math.pi))
                        self.danmaku.add(test_bullet(self.pos + [self.width / 2 + 6, self.height], direction=1.5 * math.pi))

                case "shootDown":
                    if self.bullet_CD_Timer == 0:
                        self.bullet_CD_Timer = Player.BULLET_DELAY
                        self.danmaku.add(test_bullet(self.pos + [self.width / 2 - 6, 0], direction=.5 * math.pi))
                        self.danmaku.add(test_bullet(self.pos + [self.width / 2 + 6, 0], direction=.5 * math.pi))

                case "shootLeft":
                    if self.bullet_CD_Timer == 0:
                        self.bullet_CD_Timer = Player.BULLET_DELAY
                        self.danmaku.add(test_bullet(self.pos + [self.width, self.height / 2 - 6], direction=math.pi))
                        self.danmaku.add(test_bullet(self.pos + [self.width, self.height / 2 + 6], direction=math.pi))

                case "shootRight":
                    if self.bullet_CD_Timer == 0:
                        self.bullet_CD_Timer = Player.BULLET_DELAY
                        self.danmaku.add(test_bullet(self.pos + [0, self.height / 2 - 6], direction=0))
                        self.danmaku.add(test_bullet(self.pos + [0, self.height / 2 + 6], direction=0))

        if "focus" in self.controller.actions:
            self.v /= 2.5
            self._actions.append("focus")

        self.x, self.y = [bind(i, bound_rect[0][n], bound_rect[1][n]) for n, i in enumerate((self.x, self.y) + self.v * dt)]
