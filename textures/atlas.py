from typing import Tuple, List

import pygame


class Atlas(dict):

    def __init__(self, fn: str, grid_size: Tuple[int, int], names: List[str], offsets: List[Tuple[int, int, int, int]] = None):
        super().__init__()

        atlas_image = pygame.image.load(fn)
        atlas_size = atlas_image.get_size()
        atlas_len = (atlas_size[0] // grid_size[0]) * (atlas_size[1] // grid_size[1])

        assert atlas_len == len(names)
        if offsets: assert atlas_len == len(offsets)

        i = 0
        for x in range(atlas_size[0] // grid_size[0]):
            for y in range(atlas_size[1] // grid_size[1]):
                self[names[i]] = atlas_image.subsurface((x * grid_size[0] + offsets[i][0],
                                                         y * grid_size[1] + offsets[i][1],
                                                         grid_size[0] + offsets[i][2],
                                                         grid_size[1] + offsets[i][3]))
                i += 1


if __name__ == '__main__':
    a = Atlas('character.png', (8, 8),
              ["moveRight", "moveUp", "moveLeft", "moveDown", "moveUpRight", "moveDownRight", "moveDownLeft", "moveUpLeft", "Focus"],
              [(1, 1, -1, -1)] * 9)
    print(a)
