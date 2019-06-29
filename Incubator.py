# UNUSED: COULDN'T FINISH IN TIME

from Item import Item
import time
import pokeconfig

class Incubator(Item):
    def __init__(self, **kwargs):
        self.extra_stats = 0
        self.pokemon_birth = 1
        self.timestamp_birth = 0

        if kwargs.get("bonus"):
            self.extra_stats = kwargs.get("bonus")

        if kwargs.get("pokemon"):
            self.pokemon_birth = kwargs.get("pokemon")

        if kwargs.get("timestamp"):
            self.timestamp_birth = kwargs.get("timestamp")

        self.uses = self.is_bred()

        super.__init__(**kwargs)

    def get_status(self):
        current_timestamp = time.time()

        return self.timestamp_birth - current_timestamp

    def is_bred(self):
        return self.get_status() < 0

    def get_lost_stats(self):
        if not self.is_bred():
            return 0
        return self.get_status() * PokeConfig.lostStatsMultiplierPerMinute

