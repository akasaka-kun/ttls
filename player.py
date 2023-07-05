import math

import numpy
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

        # global
        GLOBAL.TO_RENDER.extend([self, self.spirit_wheel_effect])
        GLOBAL.TO_UPDATE.extend([self, self.spirit_wheel_effect])
        GLOBAL.PLAYER = self

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
        frame_number = str(self.animation_state[1] // Player.ANIMATION_FRAME_DURATION % 5)
        return pygame.transform.scale2x(self.texture_atlas.get(current[0] + frame_number, self.default_surface))

    def spirit_wheel_surface(self):
        surf = pygame.Surface((self.width, self.height)).convert_alpha()
        surf.fill((0, 0, 0, 0))
        res = surf.copy()
        rect = pygame.Rect(self.pos, [self.height, self.width])

        if self.spirit_selection_cooldown != 0:
            angle = self.spirit_selection_cooldown / self.spirit_selection_total_cooldown * 360
            misc.arc(res, (255, 0, 255), surf.get_rect().center, surf.get_rect().width // 2, 0, angle, 3)
        if self.spirit_wheel_time > 0:
            time_factor = self.spirit_wheel_time / self.SPIRIT_WHEEL_TIME_LIMIT
            grading_angles = list(map(lambda x: x * 360 - 90, self.SPIRIT_GRADING))
            grading_mask = surf.copy()
            misc.arc(grading_mask, (000, 255, 000), surf.get_rect().center, surf.get_rect().width // 2, -90, grading_angles[0], 3)
            misc.arc(grading_mask, (255, 165, 000), surf.get_rect().center, surf.get_rect().width // 2, grading_angles[0], grading_angles[1], 3)
            misc.arc(grading_mask, (255, 000, 000), surf.get_rect().center, surf.get_rect().width // 2, grading_angles[1], 270, 3)

            spirit_wheel_timer = surf.copy()
            misc.arc(spirit_wheel_timer, (255, 255, 255), surf.get_rect().center, surf.get_rect().width // 2, -90, time_factor * 360 - 90, 3)
            spirit_wheel_timer.blit(grading_mask, [0, 0], special_flags=pygame.BLEND_MULT)
            res.blit(spirit_wheel_timer, [0, 0])

        return res, rect

    def update(self, dt):
        self._actions = []

        self.collider.rect = pygame.Rect(self.pos + (numpy.asarray([self.width, self.height]) // 2), [self.collider.size] * 2)

        for i in GLOBAL.PROJECTILE_GROUPS:
            if i.faction != self.faction:
                collisions = pygame.sprite.spritecollide(self.collider, i, True, pygame.sprite.collide_circle)
                if collisions:
                    raise Exception("Died")

        self.v.fill(0)
        self.bullet_CD_Timer = max(0, self.bullet_CD_Timer - dt)

        if self.spirit_selection_cooldown != 0:
            self.spirit_selection_cooldown = max(self.spirit_selection_cooldown - dt, 0)
        if "spirits" in self.controller.actions and self.spirit_selection_cooldown == 0:
            self.spirit_wheel_time += dt / self.SPIRIT_SLOWDOWN_FACTOR
            GLOBAL.TIME_FACTOR = self.SPIRIT_SLOWDOWN_FACTOR
            if self.spirit_wheel_time >= self.SPIRIT_WHEEL_TIME_LIMIT:
                GLOBAL.TIME_FACTOR = 1
                self.spirit_wheel_time = 0
                self.spirit_selection_cooldown = self.spirit_selection_total_cooldown = self.SPIRIT_SELECTION_BREAK_COOLDOWN
                print("broke spirit")
        elif self.spirit_wheel_time != 0 and self.spirit_selection_cooldown == 0:
            print("chose spirit")
            GLOBAL.TIME_FACTOR = 1
            self.spirit_wheel_time = 0
            self.spirit_selection_cooldown = self.spirit_selection_total_cooldown = self.SPIRIT_SELECTION_COOLDOWN

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

        if "focus" in self.controller.actions:
            self.v /= 2.5
            self._actions.append("focus")

        self.x, self.y = [bind(i, bound_rect[0][n], bound_rect[1][n]) for n, i in enumerate((self.x, self.y) + self.v * dt)]
