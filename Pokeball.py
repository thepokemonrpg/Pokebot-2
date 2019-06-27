import random
from Item import Item


class Pokeball(Item):
    def __init__(self, **kwargs):
        self.chance = 0

        if kwargs.get("chance"):
            self.chance = kwargs.get("chance")

        self.uses = self.is_successful()

        Item.__init__(self, **kwargs)

    def is_successful(self):
        return random.randint(0, 100) < self.chance

