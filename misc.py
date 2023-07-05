import pygame
from PIL import ImageDraw, Image
from numpy import array as arr


def bind(value, minV, maxV):
    return max(minV, min(maxV, value))


def arc(surf: pygame.Surface, color, center, radius, start, end, width):
    arc_surface = Image.new("RGBA", (radius * 2, radius * 2), (0, 0, 0, 0))
    draw = ImageDraw.ImageDraw(arc_surface)
    draw.arc([(0, 0), arc_surface.size], start, end, fill=color, width=width)
    surf.blit(pygame.image.fromstring(arc_surface.tobytes(), arc_surface.size, "RGBA").convert_alpha(), center - arr([radius] * 2))


def action_repeat(func):
    def wrapper(*args, duration: float):
        t = 0
        while t <= 1:
            dt = yield
            t += dt / duration
            func(*args, **{"time": t, "dt": dt})

    return wrapper
