import discord


class FightEmbedGUI:
    def __init__(self, **kwargs):
        self.challenger = kwargs.get("challenger")
        self.opponent = kwargs.get("opponent")
        self.firstMove = kwargs.get("firstMove")
        self.wild = kwargs.get("wild")

        self.challengerPokemon = kwargs.get("cpokemon")
        self.opponentPokemon = kwargs.get("opokemon")

        self.firstPokemon = kwargs.get("fpokemon")

        self.embed = discord.Embed(description="Pokemon Battle between " + str(self.challenger) + " and " + str(self.opponent) + "\n", colour=0x00ff00)

        self.embed.set_author(name="Fighting", icon_url=self.challenger.avatar_url)
        self.embed.add_field(name=str(self.challenger), value=self.challengerPokemon.get_name().title() + "\n▰▰▰▰▰▰▰▰  \nHP: **" + self.challengerPokemon.get_beauty_hp() + "**\n\n" + self.challengerPokemon.get_beauty_moves(), inline=True)
        self.embed.add_field(name=str(self.opponent), value=self.opponentPokemon.get_name().title() + "\n▰▰▰▰▰▰▰▰  \nHP: **" + self.opponentPokemon.get_beauty_hp() + "**\n\n" + self.opponentPokemon.get_beauty_moves(), inline=True)
        self.embed.add_field(name="**" + str(self.firstMove) + "**'s turn", value="Type one of the following in the chat:\n\n " + self.firstPokemon.get_beauty_moves() + "1. Use Pokeball *(Only works on Wild Pokemons)*\n2. Pokemon\n3. Escape", inline=False)

        self.embed.set_footer(text="Reply within 15 seconds when it is YOUR turn or you will automatically lose")

    def get_embed(self):
        return self.embed

    def set_move(self, user, pokemon):
        self.embed.add_field(name="**" + str(user) + "**'s turn", value="Type one of the following in the chat:\n\n " + pokemon.get_beauty_moves() + "1. Use Pokeball *(Only works on Wild Pokemons)*\n2. Pokemon\n3. Escape", inline=False)

    def update_opponent(self, index, healthString, healthBars):
        if index == 0:
            self.embed.set_field_at(0, name=str(self.challenger), value=self.challengerPokemon.get_name().title() + "\n" + healthBars + "  \nHP: **" + healthString + "**\n\n" + self.challengerPokemon.get_beauty_moves(), inline=True)
        else:
            self.embed.set_field_at(1, name=str(self.opponent), value=self.opponentPokemon.get_name().title() + "\n" + healthBars + "  \nHP: **" + healthString + "**\n\n" + self.opponentPokemon.get_beauty_moves(), inline=True)

    def add_log(self, log):
        self.embed.set_footer(text=self.embed.footer.text + log)
