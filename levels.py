from typing import Dict, List
from enemyData import TestEnemy


class LEvent:

    def __init__(self, function, args):
        self.function = function
        self.args = args

    def proc(self):
        return self.function(*self.args)


class EventGroup:
    def __init__(self, events):
        self.events = events

    def proc(self):
        for e in self.events:
            e.proc()


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


from EventGroupData import TestEnemySpawner

Default = Level({
    1: [LEvent(TestEnemy.spawn, [(0, 0)]), LEvent(TestEnemy.spawn, [(1000, 0), "right"])],
    1.3: [LEvent(TestEnemy.spawn, [(0, 0)]), LEvent(TestEnemy.spawn, [(1000, 0), "right"])],
    1.6: [LEvent(TestEnemy.spawn, [(0, 0)]), LEvent(TestEnemy.spawn, [(1000, 0), "right"])],
    1.9: [LEvent(TestEnemy.spawn, [(0, 0)]), LEvent(TestEnemy.spawn, [(1000, 0), "right"])],
    3: [LEvent(TestEnemy.spawn, [(0, 0)]), LEvent(TestEnemy.spawn, [(1000, 0), "right"])],
    3.3: [LEvent(TestEnemy.spawn, [(0, 0)]), LEvent(TestEnemy.spawn, [(1000, 0), "right"])],
    3.6: [LEvent(TestEnemy.spawn, [(0, 0)]), LEvent(TestEnemy.spawn, [(1000, 0), "right"])],
    3.9: [LEvent(TestEnemy.spawn, [(0, 0)]), LEvent(TestEnemy.spawn, [(1000, 0), "right"])],
    5: [LEvent(TestEnemy.spawn, [(0, 0)]), LEvent(TestEnemy.spawn, [(1000, 0), "right"])],
    5.3: [LEvent(TestEnemy.spawn, [(0, 0)]), LEvent(TestEnemy.spawn, [(1000, 0), "right"])],
    5.6: [LEvent(TestEnemy.spawn, [(0, 0)]), LEvent(TestEnemy.spawn, [(1000, 0), "right"])],
    5.9: [LEvent(TestEnemy.spawn, [(0, 0)]), LEvent(TestEnemy.spawn, [(1000, 0), "right"])],
    7: TestEnemySpawner([500, 0], 40, 12)
})
