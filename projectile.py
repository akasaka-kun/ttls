import abc
import math
from typing import Tuple

import pygame

import GLOBAL
import config


class Danmaku:
    """
    turns out in old testing, having projectiles as separated projectile fields per projectile type was more efficient
    """

    def __init__(self, ptype: type, faction, default_collider=("circle", 10)):
        assert issubclass(ptype, projectile)
        self.ptype = ptype
        self.default_collider = default_collider
        self.bullet_field = []

        self.faction = faction  # for now, just determines if it collides with the player or the enemies
        self.collide_with = []

        self.x, self.y = 0, 0
        GLOBAL.TO_RENDER.append(self)
        GLOBAL.TO_UPDATE.append(self)
        GLOBAL.DANMAKU_UPDATES.append(self)

    @property
    def surface(self):
        surf = pygame.Surface(config.playfield_size).convert_alpha()
        surf.fill((0, 0, 0, 0))
        for i in self.bullet_field:
            surf.blit(self.ptype.surface, i["pos"])
        return surf

    def add_bullet(self, pos, collider=None, **kwargs):
        if collider is None: collider = self.default_collider
        self.bullet_field.append({"pos": pos, "time": 0, "collider": collider, **kwargs} | self.ptype.new_bullet())

    def provide(self, collides):
        self.collide_with = [i for i in collides if i.faction != self.faction and getattr(i, "collider")]

    def update(self, dt):
        for n, i in enumerate(self.bullet_field):
            updates = self.ptype.update_pos(**i)

            # todo make this less atrociously quickfix-like
            for j in self.collide_with:
                if i["collider"][0] == "circle" and j.collider[0] == "circle":
                    if math.dist(i["pos"], j.pos) <= (i["collider"][1] + j.collider[1]):
                        print("COLLISION")
                        j.collided.append(i)
                        handle = self.ptype.on_collision()
                        match handle:
                            case "delete":
                                self.bullet_field.pop(n)

            assert updates.get("time") is None
            i.update(updates)
            i["time"] = i["time"] + dt


class projectile(abc.ABC):
    """please implement ALL class attributes in your subclasses"""
    surface: pygame.Surface
    collider: Tuple[str, ...]

    @staticmethod
    @abc.abstractmethod
    def update_pos(pos, time, **kwargs) -> dict:
        pass

    @staticmethod
    def on_collision():  # for most cases you can leave this as is
        return "delete"

    @staticmethod
    @abc.abstractmethod
    def new_bullet() -> dict:
        return {}
