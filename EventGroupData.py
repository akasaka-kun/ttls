from levels import EventGroup, LEvent
from enemyData import TestEnemy


class EnemySpawner(EventGroup):
    pass


class TestEnemySpawner(EnemySpawner):
    def __init__(self, center, spacing, count):
        self.events = [LEvent(TestEnemy.spawn, [[center[0] + (i+0.5 - count / 2) * spacing, center[1]], "forward"]) for i in range(count)]
        super().__init__(self.events)
