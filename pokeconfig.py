class PokeConfig:
    token = ""
    rewardsTimer = 1 * 60 * 60 * 24  # 24 hours cooldown between daily rewards
    plrReward = 500  # Daily reward amount is set here
    startingGold = 500  # Gold given when a player starts
    startingPokemon = [1, 4, 7]  # 1 = Bulbasaur, 4 = Charmander, 7 = Squirtle
    lostStatsMultiplierPerMinute = 2  # Every minute X stats will be removed. Make it 0 if you want to disable this feature
    shopItems = [
        {
            "id": 0,
            "name": "Normal Pokeball",
            "cost": 100,
            "category": "pokeball",
            "chance": 30,
            "description": "You have a 30% chance to catch a pokemon when you use this item!"
        },
        {
            "id": 1,
            "name": "Super Pokeball",
            "cost": 500,
            "category": "pokeball",
            "chance": 75,
            "description": "You have a 75% chance to catch a pokemon when you use this item!"
        }
    ]
