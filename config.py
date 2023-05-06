import pygame

# user configs
size = (800, 800)
keyboard_controls = {
    pygame.K_w: "up",
    pygame.K_a: "left",
    pygame.K_s: "down",
    pygame.K_d: "right",
    pygame.K_LSHIFT: "focus"
}

# game configs
playfield_size = (1000, 1000)
bound_rect = ((100, 100), (900, 900))
