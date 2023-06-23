from typing import Dict, Tuple, FrozenSet


class animation:
    pass


class animation_atlas(dict):
    def __init__(self, **kwargs: animation):
        """this is not necessary and will work exactly like a dict, it is here to provide clarity. when taking the state and applying the animation, you will be asking the animation atlas which animation corresponds to a given state."""
        assert all(isinstance(i, animation) for i in kwargs.values()), "please only use animation class instances as animations"
        super().__init__(**kwargs)
