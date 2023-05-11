import abc

import pygame

import GLOBAL
import config


class Danmaku:
    """
    turns out in old testing, having projectiles as separated projectile fields per projectile type was more efficient
    """

    def __init__(self, ptype: type, faction):
        assert issubclass(ptype, projectile)
        self.ptype = ptype
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

    def add_bullet(self, pos, **kwargs):
        self.bullet_field.append({"pos": pos, "time": 0, **kwargs})

    def provide(self, collides):
        self.collide_with = [i for i in collides if i.faction != self.faction]

    def update(self, dt):
        for i in self.bullet_field:
            updates = self.ptype.update_pos(**i)
            assert updates.get("time") is None
            i.update(updates)
            i["time"] = i["time"] + dt


class projectile(abc.ABC):
    surface: pygame.Surface

    @staticmethod
    @abc.abstractmethod
    def update_pos(pos, time, **kwargs) -> dict:
        pass
