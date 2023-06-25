from typing import Dict, List
from enemies import TestEnemy


class LEvent:

    def __init__(self, function, args):
        self.function = function
        self.args = args

    def proc(self):
        return self.function(*self.args)


class Level:

    def __init__(self, events: Dict[float, List[LEvent] | LEvent]):
        self.events = events

    def proc_events(self, time):
        to_remove = []
        for t in self.events:
            if t <= time:
                to_proc = self.events[t]
                to_remove.append(t)
                if isinstance(to_proc, list):
                    [e.proc() for e in to_proc]
                else:
                    to_proc.proc()
        for k in to_remove:
            self.events.pop(k)


# todo change levels system to allow multiple simultaneous events
Default = Level({
    1: LEvent(TestEnemy.spawn, [(200, 100)]),
    1.3: LEvent(TestEnemy.spawn, [(400, 100)]),
    1.6: LEvent(TestEnemy.spawn, [(600, 100)]),
    1.9: LEvent(TestEnemy.spawn, [(800, 100)]),
    3: LEvent(TestEnemy.spawn, [(200, 100)]),
    3.3: LEvent(TestEnemy.spawn, [(400, 100)]),
    3.6: LEvent(TestEnemy.spawn, [(600, 100)]),
    3.9: LEvent(TestEnemy.spawn, [(800, 100)]),
    5: LEvent(TestEnemy.spawn, [(200, 100)]),
    5.3: LEvent(TestEnemy.spawn, [(400, 100)]),
    5.6: LEvent(TestEnemy.spawn, [(600, 100)]),
    5.9: LEvent(TestEnemy.spawn, [(800, 100)]),
})
