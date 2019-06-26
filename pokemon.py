from pprint import pprint
import pokepy

client = pokepy.V2Client()

def get_pokemon_name(pokemon_name):
    pokemon = client.get_pokemon(pokemon_name)
    return pokemon.name

def get_pokemon_abilities(pokemon_name):
    pokemon = client.get_pokemon(pokemon_name)
    list = []
    abilities = pokemon.stats
    length = len(abilities)
    for i in range(length):
        list.append(abilities[i].stat.name)

    return list

def get_pokemon_moves(pokemon_name):
    pokemon = client.get_pokemon(pokemon_name)
    return pokemon.moves

def get_pokemon_stats(pokemon_name):
    pokemon = client.get_pokemon(pokemon_name)
    return pokemon.stats

def get_pokemon_cost(pokemon_name):
    pokemon = client.get_pokemon(pokemon_name)
    abilities = pokemon.stats
    length = len(abilities)
    total = 0
    for i in range(length):
        total += abilities[i].base_stat

    return total*2

def get_pokemon_potential_abilities(pokemon_name):
    pokemon = client.get_pokemon(pokemon_name)
    return pokemon.abilities

if __name__ == '__main__':
    get_pokemon_cost("ditto")
