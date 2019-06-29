from pprint import pprint
import pokepy
import random

client = pokepy.V2Client()
damageTypeModifiers = {
    "normal": {
        "ghost": 0,
        "rock": 0.5,
        "steel": 0.5
    },

    "fighting": {
        "normal": 2,
        "flying": 0.5,
        "poison": 0.5,
        "rock": 2,
        "bug": 0.5,
        "ghost": 0,
        "psychic": 0.5,
        "steel": 2,
        "ice": 2,
        "dark": 2,
        "fairy": 0.5
    },

    "flying": {
        "fighting": 2,
        "rock": 0.5,
        "bug": 2,
        "steel": 0.5,
        "grass": 2,
        "electric": 0.5
    },

    "poison": {
        "poison": 0.5,
        "ground": 0.5,
        "rock": 0.5,
        "ghost": 0.5,
        "steel": 0,
        "grass": 2,
        "fairy": 2
    },

    "ground": {
        "flying": 0,
        "poison": 2,
        "rock": 2,
        "bug": 0.5,
        "steel": 2,
        "fire": 2,
        "grass": 0.5,
        "fairy": 2
    },

    "rock": {
        "fighting": 0.5,
        "flying": 2,
        "ground": 0.5,
        "bug": 2,
        "steel": 0.5,
        "fire": 2,
        "ice": 2
    },

    "bug": {
        "fighting": 0.5,
        "flying": 0.5,
        "poison": 0.5,
        "ghost": 0.5,
        "steel": 0.5,
        "fire": 0.5,
        "grass": 2,
        "psychic": 2,
        "dark": 2,
        "fairy": 0.5
    },

    "ghost": {
        "normal": 0,
        "ghost": 2,
        "psychic": 2,
        "dark": 0.5
    },

    "steel": {
        "rock": 2,
        "steel": 0.5,
        "fire": 0.5,
        "water": 0.5,
        "electric": 0.5,
        "ice": 2,
        "fairy": 2
    },

    "fire": {
        "rock": 0.5,
        "bug": 2,
        "steel": 2,
        "fire": 0.5,
        "water": 0.5,
        "grass": 2,
        "ice": 2,
        "dragon": 0.5
    },

    "water": {
        "ground": 2,
        "rock": 2,
        "fire": 2,
        "water": 0.5,
        "grass": 0.5,
        "dragon": 0.5
    },

    "grass": {
        "flying": 0.5,
        "poison": 0.5,
        "ground": 2,
        "rock": 2,
        "bug": 0.5,
        "steel": 0.5,
        "fire": 0.5,
        "water": 2,
        "grass": 0.5,
        "dragon": 0.5
    },

    "electric": {
        "flying": 2,
        "ground": 0,
        "water": 2,
        "grass": 0.5,
        "electric": 0.5,
        "dragon": 0.5
    },

    "psychic": {
        "fighting": 2,
        "poison": 2,
        "steel": 0.5,
        "psychic": 0.5,
        "dark": 0
    },

    "ice": {
        "flying": 2,
        "ground": 2,
        "steel": 0.5,
        "fire": 0.5,
        "water": 0.5,
        "grass": 2,
        "ice": 0.5,
        "dragon": 2
    },

    "dragon": {
        "steel": 0.5,
        "ice": 2,
        "fairy": 0
    },

    "dark": {
        "fighting": 0.5,
        "ghost": 2,
        "psychic": 2,
        "dark": 0.5,
        "fairy": 0.5
    },

    "fairy": {
        "fighting": 2,
        "poison": 0.5,
        "steel": 0.5,
        "fire": 0.5,
        "dragon": 2,
        "dark": 2
    }
}


class BadArgumentError(Exception):
    pass


class DamageModifier:
    def __init__(self, **kwargs):
        if kwargs.get("type"):
            self.type = kwargs.get("type")
        else:
            raise BadArgumentError("Invalid type")

        self.criticalModifier = True
        self.modifiers = []

        for i in self.type:
            self.modifiers.append(damageTypeModifiers.get(i))

        if kwargs.get("disableCritical"):
            self.criticalModifier = False

    def get_type_modifier(self, another_type):
        damage = 1

        for i in self.modifiers:
            if another_type in i:
                damage = damage + i.get(another_type)

        return damage

    def get_critical_modifier(self):
        if not self.criticalModifier:
            return 1
        return round(random.randint(217, 255) / 255)

    def get_stab_modifier(self, move_type):  # STAB = Same Type Attack Bonus, where in attack type is same as pokemon type
        if move_type in self.type:
            return 1.5
        return 1

    def get_move_damage(self, power, attack_stat, level, move_type, opponent_types, opponent_defence, wild=False):
        typeModifier = 1

        for i in opponent_types:
            typeModifier = typeModifier + self.get_type_modifier(i)

        levelDmg = ((2 + ((2*level)/5)) * power * (attack_stat/opponent_defence))/50
        modifier = self.get_critical_modifier() * typeModifier * self.get_stab_modifier(move_type)
        damage = levelDmg + 2

        if modifier > 2:
            modifier = 2

        if modifier < 0.5:
            modifier = 0.5

        if wild and level < 15:
            modifier = 0.75

        damage = damage * modifier
        return damage


class Pokemon:
    def __init__(self, **kwargs):
        if kwargs.get("name"):
            self.pokemon = client.get_pokemon(kwargs.get("name"))
        elif kwargs.get("id") and isinstance(kwargs.get("id"), int):
            self.pokemon = client.get_pokemon(kwargs.get("id"))
        else:
            raise BadArgumentError("Invalid arguments passed on")

        self.real = False
        self.level = 0
        self.usermoves = []
        self.owner = ""
        self.uniqueID = 0
        self.xp = 0

        if kwargs.get("xp"):
            self.xp = kwargs.get("xp")

        if kwargs.get("unique"):
            self.uniqueID = kwargs.get("unique")

        if kwargs.get("real"):
            self.real = True

        if kwargs.get("level"):
            self.level = kwargs.get("level")

        if kwargs.get("moves"):
            currentmoves = kwargs.get("moves")

            self.usermoves = currentmoves

            if isinstance(currentmoves, str):
                self.usermoves = kwargs.get("moves").split(",")

        if kwargs.get("owner"):
            self.owner = kwargs.get("owner")

        self.stats = []
        statistics = self.pokemon.stats
        stats_length = len(statistics)
        for i in range(stats_length):
            self.stats.append(statistics[i].stat.name)

        self.moves = self.pokemon.moves
        self.pokemonTypes = []
        self.stats = self.pokemon.stats

        for i in self.pokemon.types:
            self.pokemonTypes.append(i.type.name)

        self.cost = 0

        for i in range(stats_length):
            self.cost += statistics[i].base_stat
        self.cost = self.cost * 2

        self.abilities = self.pokemon.abilities

    def get_type(self):
        return self.pokemonTypes

    def get_unique_id(self):
        return self.uniqueID

    def is_trained_owner(self):
        return self.real

    def get_name(self):
        return self.pokemon.name

    def get_id(self):
        return self.pokemon.game_indices[0].game_index

    def get_moves(self):
        if len(self.usermoves) > 0:
            return self.usermoves
        return self.moves

    def get_base_stats(self):
        return self.stats

    def get_move(self, move):
        return client.get_move(move)

    def get_stats(self, level):
        new_statistics = []

        stats_length = len(self.pokemon.stats)
        increase_in_stat = level * (1/50)

        if self.real:
            increase_in_stat = increase_in_stat * 2

        for i in range(stats_length):
            if self.pokemon.stats[i].stat.name == "hp":
                new_statistics.append({self.pokemon.stats[i].stat.name: self.pokemon.stats[i].base_stat + (increase_in_stat * 100)})
            else:
                new_statistics.append({self.pokemon.stats[i].stat.name: (self.pokemon.stats[i].base_stat + increase_in_stat)})

        return new_statistics

    def get_cost(self):
        return self.cost

    def get_potential_abilities(self):
        return self.abilities

    def get_starting_moves(self):
        moves = []

        current_moves = self.moves

        for i in current_moves:
            if len(moves) == 4:
                 break

            for version in i.version_group_details:
                if (not i.move.name in moves) and version.version_group.name == "red-blue" and version.level_learned_at <= 1 and version.move_learn_method.name == "level-up":
                       moves.append(i.move.name)

        return moves

    def get_wild_moves(self):
        moves = []

        current_moves = self.moves

        for i in reversed(current_moves):
            if len(moves) == 4:
                break

            for version in i.version_group_details:
                if (not i.move.name in moves) and version.version_group.name == "red-blue" and version.level_learned_at <= self.level and version.move_learn_method.name == "level-up":
                    moves.append(i.move.name)
        return moves

    def get_new_moves(self, level=1):
        moves = []

        current_moves = self.moves

        for i in reversed(current_moves):
            for version in i.version_group_details:
                if (not i.move.name in moves) and version.version_group.name == "red-blue" and version.level_learned_at == level and version.move_learn_method.name == "level-up":
                    moves.append(i.move.name)

        return moves

    def get_level(self):
        return self.level

    def get_beauty_hp(self, level=1):
        hp = str(self.get_stat("hp", level))

        return hp + "/" + hp

    def get_stat(self, stat, level=1):
        stats = self.get_stats(level)

        for i in stats:
            if stat in i:
                return i[stat]

        return ""

    def get_beauty_moves(self):
        moves = self.get_wild_moves()

        if len(self.usermoves) > 0:
            moves = self.usermoves

        beauty_moves = ""

        for i, v in enumerate(moves):
            beauty_moves = beauty_moves + (chr(97 + i) + ". " + v.title() + "\n")

        return beauty_moves

    def get_exp(self):
        return self.xp

    def get_exp_for_levelup(self):
        return (20 * self.level) + 50
