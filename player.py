import math

import numpy
import numpy as np
import pygame
from pygame import gfxdraw

import misc
import projectile
from misc import bind
from config import bound_rect

import GLOBAL
from render import Renderable
from textures.atlas import Atlas
from collision import collider_sprite
from vfx import Vfx


class test_bullet(projectile.Projectile):
    SPEED = 2000
    (IMAGE := pygame.Surface((3, 10))).fill((255, 0, 0))

    def __init__(self, pos, direction):
        self.direction = direction
        self.scalars = numpy.array([math.cos(self.direction), math.sin(self.direction)], dtype=float)
        self.image = pygame.transform.rotate(test_bullet.IMAGE, direction * (180 / math.pi) + 90)
        self.damage = 15
        super().__init__(numpy.array(pos) - numpy.array(self.image.get_size()) // 2, [10, 20])

    def update(self, dt):
        self.pos = self.pos + (self.scalars * (dt * test_bullet.SPEED))


class Player(Renderable):
    BULLET_DELAY = .050
    V = 400

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

    SPIRIT_WHEEL_TIME_LIMIT = 2
    SPIRIT_SELECTION_BREAK_COOLDOWN = 10
    SPIRIT_SELECTION_COOLDOWN = 3
    SPIRIT_SELECTION_COYOTE_TIME = 3
    SPIRIT_SLOWDOWN_FACTOR = .3
    SPIRIT_GRADING = [.25, .66]

    def __init__(self, controller):
        self.controller = controller

        # movement stuff
        self.v = numpy.zeros(2, dtype=float)
        self.x = 500
        self.y = 800

        # collision with bullets stuff
        self.faction = "player"
        self.danmaku = projectile.Danmaku(self.faction)
        self.bullet_CD_Timer = 0
        self.collider = collider_sprite(2)

        # animation stuff
        self.width, self.height = 40, 40
        self.default_surface = [(S := pygame.Surface((self.width / 2, self.height / 2))).convert_alpha(), S.fill((255, 0, 0, 255)), S][-1]
        self.animation_state = ("", 1)
        self.texture_atlas = Atlas('textures/character.png', (22, 20),
                                   [i + str(j) for j in range(5) for i in ["moveRight", "moveDown", "moveLeft", "moveUp", "moveUpRight", "moveDownRight", "moveDownLeft", "moveUpLeft", "Focus", "idle"]],
                                   [(0, 0, -1, 0)] * 10 * 5)
        self._actions = []

        # spirit selection stuff
        self.spirit_wheel_time = 0
        self.spirit_selection_cooldown = 0
        self.spirit_selection_total_cooldown = 0
        self.spirit_wheel_effect = Vfx(self.spirit_wheel_surface)

        self.spirit_wheel_slice = pygame.image.load("textures/spirit selection slice.png")
        self.spirit_wheel_slice = pygame.transform.scale(pygame.image.load("textures/spirit selection slice.png"), np.array(self.spirit_wheel_slice.get_size()) * 0.16)

        self.selecting_spirit = ""
        self.spirit_selection_coyote_time = self.SPIRIT_SELECTION_COYOTE_TIME
        self.spirit = ""

        # global
        GLOBAL.TO_RENDER.extend([self, self.spirit_wheel_effect])
        GLOBAL.TO_UPDATE.extend([self, self.spirit_wheel_effect])
        GLOBAL.PLAYER = self

    @property
    def pos(self):
        return numpy.array([self.x, self.y])

    @property
    def surface(self):
        current = self._state_to_animation_state(self._actions)
        self.animation_state = current[0], 0 if current[0] != self.animation_state[0] else (self.animation_state[1] + 1)
        frame_number = str(self.animation_state[1] // Player.ANIMATION_FRAME_DURATION % 5)
        return pygame.transform.scale2x(self.texture_atlas.get(current[0] + frame_number, self.default_surface))

    @staticmethod
    def _state_to_animation_state(states):
        current = ("idle", 0)
        for c, s in Player.ANIMATION_STATES.items():
            if all(i in states for i in c):
                prio = s[1] + sum(n for n, a in enumerate(states) if a in c)
                if current[1] < prio:
                    current = s[0], prio
        return current

    def spirit_wheel_surface(self):
        if self.spirit_wheel_time == 0 and self.spirit_selection_cooldown == 0:
            return pygame.Surface((0, 0)), pygame.Rect([0, 0, 0, 0])

        offset = numpy.array([25, 25])
        rect = pygame.Rect(self.pos - offset, [self.width, self.height] + offset * 2)
        surf = pygame.Surface(rect.size).convert_alpha()
        surf.fill((0, 0, 0, 0))
        res = surf.copy()

        player_rect = self.surface.get_rect()

        if self.spirit_selection_cooldown != 0:
            misc.arc(res, (200, 0, 0), res.get_rect().center, 25, -90, -90 + (self.spirit_selection_cooldown / self.spirit_selection_total_cooldown) * 360, 3)
            return res, rect

        directionToSlice = {"spiritSelectUp": 3, "spiritSelectUpRight": 2, "spiritSelectDownRight": 1, "spiritSelectDown": 0, "spiritSelectDownLeft": 5, "spiritSelectUpLeft": 4}
        for i in range(6):
            rotated = pygame.transform.rotate(self.spirit_wheel_slice, 60 * (i + 3))
            print(self.selecting_spirit, directionToSlice[self.selecting_spirit])
            if directionToSlice[self.selecting_spirit] == i: rotated = pygame.transform.scale(rotated, np.array(rotated.get_size()) * 1.4)
            res.blit(rotated, res.get_rect().center + np.multiply((math.sin(i / 3 * math.pi), math.cos(i / 3 * math.pi)), [30, 30]) + [0, 0] - np.divide(rotated.get_size(), 2))

        return res, rect

    def update(self, dt):
        self._actions = []
        reset_v = True

        self.collider.rect = pygame.Rect(self.pos + (numpy.asarray([self.width, self.height]) // 2), [self.collider.size] * 2)

        for i in GLOBAL.PROJECTILE_GROUPS:
            if i.faction != self.faction:
                collisions = pygame.sprite.spritecollide(self.collider, i, True, pygame.sprite.collide_circle)
                if collisions:
                    raise Exception("Died")

        if self.spirit_selection_cooldown != 0:
            self.spirit_selection_cooldown = max(self.spirit_selection_cooldown - dt, 0)

        if reset_v: self.v.fill(0)
        self.bullet_CD_Timer = max(0, self.bullet_CD_Timer - dt)

        for a in self.controller.actions:

            match a:

                # move
                case "up":
                    self.v[1] = -Player.V
                    self._actions.append("moveUp")
                case "left":
                    self.v[0] = -Player.V
                    self._actions.append("moveLeft")
                case "down":
                    self.v[1] = Player.V
                    self._actions.append("moveDown")
                case "right":
                    self.v[0] = Player.V
                    self._actions.append("moveRight")

                # shoot
                case "shootUp":
                    if self.bullet_CD_Timer == 0:
                        self.bullet_CD_Timer = Player.BULLET_DELAY
                        self.danmaku.add(test_bullet(self.pos + [self.width / 2 - 6, self.height * .25], direction=1.5 * math.pi))
                        self.danmaku.add(test_bullet(self.pos + [self.width / 2 + 6, self.height * .25], direction=1.5 * math.pi))

                case "shootDown":
                    if self.bullet_CD_Timer == 0:
                        self.bullet_CD_Timer = Player.BULLET_DELAY
                        self.danmaku.add(test_bullet(self.pos + [self.width / 2 - 6, self.height * .75], direction=.5 * math.pi))
                        self.danmaku.add(test_bullet(self.pos + [self.width / 2 + 6, self.height * .75], direction=.5 * math.pi))

                case "shootLeft":
                    if self.bullet_CD_Timer == 0:
                        self.bullet_CD_Timer = Player.BULLET_DELAY
                        self.danmaku.add(test_bullet(self.pos + [self.width * .25, self.height / 2 - 6], direction=math.pi))
                        self.danmaku.add(test_bullet(self.pos + [self.width * .25, self.height / 2 + 6], direction=math.pi))

                case "shootRight":
                    if self.bullet_CD_Timer == 0:
                        self.bullet_CD_Timer = Player.BULLET_DELAY
                        self.danmaku.add(test_bullet(self.pos + [self.width * .75, self.height / 2 - 6], direction=0))
                        self.danmaku.add(test_bullet(self.pos + [self.width * .75, self.height / 2 + 6], direction=0))

                case "spirits":

                    if self.spirit_selection_cooldown == 0:
                        self.spirit_wheel_time += dt / self.SPIRIT_SLOWDOWN_FACTOR
                        GLOBAL.TIME_FACTOR = self.SPIRIT_SLOWDOWN_FACTOR

                        if self.spirit_wheel_time >= self.SPIRIT_WHEEL_TIME_LIMIT:
                            self.spirit = ""
                            GLOBAL.TIME_FACTOR = 1
                            self.spirit_wheel_time = 0
                            self.spirit_selection_cooldown = self.spirit_selection_total_cooldown = self.SPIRIT_SELECTION_BREAK_COOLDOWN
                            print("broke spirit")
                    else:
                        continue

                    for direction in self.controller.actions:
                        if direction not in ["up", "left", "down", "right"]:
                            continue
                        print(direction)
                        match direction:
                            case "left" if "up" in self.controller.actions:
                                self.selecting_spirit = "spiritSelectUpLeft"
                            case "right" if "up" in self.controller.actions:
                                self.selecting_spirit = "spiritSelectUpRight"
                            case "left" if "down" in self.controller.actions:
                                self.selecting_spirit = "spiritSelectDownLeft"
                            case "right" if "down" in self.controller.actions:
                                self.selecting_spirit = "spiritSelectDownRight"
                            case "up" if not any(i in self.controller.actions for i in ["left", "right"]):
                                self.selecting_spirit = "spiritSelectUp"
                            case "down" if not any(i in self.controller.actions for i in ["left", "right"]):
                                self.selecting_spirit = "spiritSelectDown"

            if self.spirit_wheel_time != 0 and self.spirit_selection_cooldown == 0 and "spirits" not in self.controller.actions:
                print("chose spirit")
                self.spirit = self.selecting_spirit
                GLOBAL.TIME_FACTOR = 1
                self.spirit_wheel_time = 0
                self.spirit_selection_cooldown = self.spirit_selection_total_cooldown = self.SPIRIT_SELECTION_COOLDOWN

        if "focus" in self.controller.actions:
            self.v /= 2.5
            self._actions.append("focus")

        self.x, self.y = [bind(i, bound_rect[0][n], bound_rect[1][n]) for n, i in enumerate((self.x, self.y) + self.v * dt)]
