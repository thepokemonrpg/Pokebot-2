import discord
from player import Player
from discord.ext import commands


@bot.command(pass_context=True, aliases=['equip'])
async def equip(ctx):
    player = Player(ctx.message.author.id)
    list = []
    id_list = []
    list = player.get_pokemon_list()
    for pokemon in list:
        id_list[pokemon] = list[pokemon.get_id()]

    if ctx in id_list:
        return "no idea wtf i am doing"






