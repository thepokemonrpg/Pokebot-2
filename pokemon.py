from pprint import pprint
import pokepy

client = pokepy.V2Client()


class BadArgumentError(Exception):
    pass


class Pokemon:
    def __init__(self, **kwargs):
        if kwargs.get("name") is str:
            self.pokemon = client.get_pokemon(kwargs.get("name"))
        elif kwargs.get("id") is int:
            self.pokemon = client.get_pokemon(kwargs.get("id"))
        else:
            raise BadArgumentError("Invalid arguments passed on")

        self.stats = []
        statistics = self.pokemon.stats
        statsLength = len(statistics)
        for i in range(statsLength):
            self.stats.append(statistics[i].stat.name)

        self.moves = self.pokemon.moves

        self.stats = self.pokemon.stats

        self.cost = 0

        for i in range(statsLength):
            self.cost += statistics[i].base_stat
        self.cost = self.cost * 2

        self.abilities = self.pokemon.abilities

    def get_pokemon_name(self):
        return self.pokemon.name

    def get_pokemon_moves(self):
        return self.moves

    def get_pokemon_stats(self):
        return self.stats

    def get_pokemon_cost(self):
        return self.cost

    def get_pokemon_potential_abilities(self):
        return self.abilities
