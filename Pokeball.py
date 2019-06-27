import random
from Item import Item



class Pokeball(Item):
    def __init__(self, **kwargs):
        Item.__init__(self, **kwargs)

    def calc_chance(self):
        if random.randint(0,100) < 50:
            print("catches")
        else:
            print("doesn't catch")






