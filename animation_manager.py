from typing import Dict, Tuple, FrozenSet


class state_manager:

    def __init__(self, states: Dict[FrozenSet[str], Tuple[str, int]]):
        f"""
        states: a dict with the condition for the state to be applied and a priority for animation that are more important (eg : if we have the state moving up and moving left and moving up-left we want the up left animation to take prio)\n
        -----------------------\n
        eg : {{frozenset(["moving up"]): ("moving up", 1),
        frozenset(["moving left"]): ("moving up", 1),
        frozenset(["moving up", "moving left"]): ("moving up-left", 2)}}

        here if both moving up and moving left actions are ongoing we will prioritize the moving up-left state
        """
        self.states = states

    def get_state(self, actions):
        current = ("none", 0)
        for c, s in self.states.items():
            if all(i in actions for i in c):
                if current[1] < s[1]:
                    current = s
        return current[0]


class animation:
    pass


class animation_atlas(dict):
    def __init__(self, **kwargs: animation):
        """this is not necessary and will work exactly like a dict, it is here to provide clarity. when taking the state and applying the animation, you will be asking the animation atlas which animation corresponds to a given state."""
        assert all(isinstance(i, animation) for i in kwargs.values()), "please only use animation class instances as animations"
        super().__init__(**kwargs)
