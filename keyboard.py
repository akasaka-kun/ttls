from config import keyboard_controls
import pygame


class Controller:

    def __init__(self, controller, controls, instances):
        self.controller = controller
        self.actions = {}
        self.controls = controls
        instances.append(self)


class Keyboard(Controller):
    instances = []

    def __init__(self):
        super(Keyboard, self).__init__('Keyboard', keyboard_controls, self.__class__.instances)

    def update(self):
        for k, c in self.controls.items():
            if pygame.key.get_pressed()[k]:
                state = self.actions.get(c, [False, 0])
                hold_time = state[1] + 1
                self.actions[c] = (bool(hold_time - 1), hold_time)
            elif self.actions.get(c, False):
                self.actions.pop(c)
