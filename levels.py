from typing import Dict
from enemies import TestEnemy


class LEvent:

    def __init__(self, function, args):
        self.function = function
        self.args = args

    def proc(self):
        return self.function(*self.args)


# todo change levels system to allow multiple simultaneous events
Default: Dict[float, LEvent] = {
    1.5: LEvent(TestEnemy.spawn, [(200, 100)]),
    1.6: LEvent(TestEnemy.spawn, [(400, 100)]),
    1.7: LEvent(TestEnemy.spawn, [(600, 100)]),
    1.8: LEvent(TestEnemy.spawn, [(800, 100)])
}
