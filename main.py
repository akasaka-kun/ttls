import pygame
import GLOBAL
import levels

from render import render
from config import size
from player import Player
from keyboard import Keyboard

pygame.init()

screen = pygame.display.set_mode(size, pygame.SRCALPHA)
version = "0.1.0"
pygame.display.set_caption(f"Touhou: The Lost Spirits v{version}")

clk = pygame.time.Clock()

keyboard = Keyboard()
player = Player(keyboard)

time = 0

while True:

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            raise Exception("Quit")
    for K in Keyboard.instances:
        K.update()

    dt = clk.tick(60) / 1000  # todo maybe independent tick rate
    time += dt

    for t in list(levels.Default):
        if t < time:
            levels.Default.pop(t).proc()

    for i in GLOBAL.TO_UPDATE:
        i.update(dt)

    screen.fill((32, 32, 32))
    for i in GLOBAL.PROJECTILE_GROUPS:  # todo put that shit in the renderer
        i.draw(screen)
    screen.blit(render(GLOBAL.TO_RENDER), (0, 0))  # todo camera pos, either here or in render
    pygame.display.flip()
