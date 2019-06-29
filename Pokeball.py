import random
from Item import Item


class Pokeball(Item):
    def __init__(self, **kwargs):
        self.chance = 0

        if kwargs.get("chance"):
            self.chance = int(kwargs.get("chance"))

        Item.__init__(self, **kwargs)

    def is_successful(self):
        return random.randint(0, 100) <= self.chance

