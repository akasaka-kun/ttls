import pygame
import pygame.gfxdraw
from PIL import ImageDraw, Image
from numpy import array as arr
from math import sqrt, cos, pi, atan2, sin, dist


def bind(value, minV, maxV):
    return max(minV, min(maxV, value))


def arc(surf: pygame.Surface, color, center, radius, start, end, width):
    arc_surface = Image.new("RGBA", (radius * 2, radius * 2), (0, 0, 0, 0))
    draw = ImageDraw.ImageDraw(arc_surface)
    draw.arc([(0, 0), arc_surface.size], start, end, fill=color, width=width)
    surf.blit(pygame.image.fromstring(arc_surface.tobytes(), arc_surface.size, "RGBA").convert_alpha(), center - arr([radius] * 2))


def line(surf, color, start, end, width):
    X0 = arr(start)
    X1 = arr(end)
    center_L1 = (X0 + X1) / 2.

    length = dist(X0, X1)  # Total length of line
    thickness = width
    angle = atan2(X0[1] - X1[1], X0[0] - X1[0])

    UL = (center_L1[0] + (length / 2.) * cos(angle) - (thickness / 2.) * sin(angle),
          center_L1[1] + (thickness / 2.) * cos(angle) + (length / 2.) * sin(angle))
    UR = (center_L1[0] - (length / 2.) * cos(angle) - (thickness / 2.) * sin(angle),
          center_L1[1] + (thickness / 2.) * cos(angle) - (length / 2.) * sin(angle))
    BL = (center_L1[0] + (length / 2.) * cos(angle) + (thickness / 2.) * sin(angle),
          center_L1[1] - (thickness / 2.) * cos(angle) + (length / 2.) * sin(angle))
    BR = (center_L1[0] - (length / 2.) * cos(angle) + (thickness / 2.) * sin(angle),
          center_L1[1] - (thickness / 2.) * cos(angle) - (length / 2.) * sin(angle))

    pygame.gfxdraw.aapolygon(surf, (UL, UR, BR, BL), color)
    pygame.gfxdraw.filled_polygon(surf, (UL, UR, BR, BL), color)


def action_repeat(func):
    def wrapper(*args, duration: float, **kwargs):
        t = 0
        while t <= 1:
            dt = yield
            t += dt / duration
            func(*args, **{"time": t, "dt": dt}, **kwargs)

    return wrapper


def easeOutCirc(x):
    return sqrt(1 - (x - 1) ** 2)


def easeInOutSine(x):
    return -(cos(pi * x) - 1) / 2
