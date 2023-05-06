from typing import Dict
from enemies import TestEnemy


class LEvent:

    def __init__(self, function, args):
        self.function = function
        self.args = args

    def proc(self):
        return self.function(*self.args)


Default: Dict[float, LEvent] = {
    1.5: LEvent(TestEnemy.spawn, [(50, 50)])
}
