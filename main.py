import discord
from discord.ext import commands, tasks
from discord.ui import button

import requests
import random

# Enable the necessary intents
intents = discord.Intents.all()

# Prefix for commands
prefix = 'l.'
bot = commands.Bot(command_prefix=prefix, intents=intents)
bot.remove_command("help")

# PokeAPI base URL
pokeapi_base_url = "https://pokeapi.co/api/v2/pokemon/"

# Shop items (name, price)
shop_items = {'<:pokeball:1179858493822476450> Poke Ball': 10, '<:greatball:1179858490735480862> Great Ball': 20, '<:ultraball:1179858488827052062> Ultra Ball': 30}
user_inventory = {}

# Currency system
user_coins = {}

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

# Catch command
@bot.command(name='catch', help='Catch a random wild Pokemon using a Poke Ball!')
async def catch(ctx):
    # Check if the user has a Poke Ball
    if '<:pokeball:1179858493822476450> Poke Ball' not in user_inventory[ctx.author.id]:
        return await ctx.send("You need a Poke Ball to catch Pokemon. Buy one from the shop with `l.buy`!")

    # Consume a Poke Ball
    remove_item(ctx.author.id, '<:pokeball:1179858493822476450> Poke Ball')

    # Generate a random Pokemon ID between 1 and 1016
    random_pokemon_id = random.randint(1, 1016)

    # Get Pokemon data from PokeAPI
    response = requests.get(pokeapi_base_url + str(random_pokemon_id))
    if response.status_code == 200:
        pokemon_data = response.json()

        # Generate a random chance for shiny or escape
        shiny_chance = random.randint(1, 10)
        escape_chance = random.randint(1, 10)

        # Create an embed with Pokemon information
        embed = discord.Embed(title=f"Wild {pokemon_data['name'].capitalize()} appeared!",
                              color=discord.Color.blue())
        embed.set_thumbnail(url=pokemon_data['sprites']['front_default'])

        # Check if the Pokemon is shiny or escaped
        if shiny_chance == 1:
            embed.add_field(name='Result', value="Congratulations! You caught a shiny Pokemon!")
        elif escape_chance == 1:
            embed.add_field(name='Result', value=f"Oh no! {pokemon_data['name'].capitalize()} escaped!")
        else:
            # Earn coins based on the Pokemon's base experience
            earn_coins = pokemon_data['base_experience'] // 10
            add_coins(ctx.author.id, earn_coins)
            embed.add_field(name='Result', value=f"You caught {pokemon_data['name'].capitalize()} and earned {earn_coins} Poke Dollars!")

        # Send the embed
        await ctx.send(embed=embed)

    else:
        await ctx.send(embed=discord.Embed(description=f"Failed to catch a random Pokemon.",
                                           color=discord.Color.red()))

# Pokedex command
@bot.command(name='pokedex', help='Get information about a Pokemon from the Pokedex')
async def pokedex(ctx, pokemon_name):
    # Get Pokemon data from PokeAPI
    response = requests.get(pokeapi_base_url + pokemon_name.lower())
    if response.status_code == 200:
        pokemon_data = response.json()

        # Create an embed with Pokemon information
        embed = discord.Embed(title=f"{pokemon_name.capitalize()}'s Pokedex Entry",
                              color=discord.Color.green())
        embed.add_field(name='Height', value=f"{pokemon_data['height'] / 10} m")
        embed.add_field(name='Weight', value=f"{pokemon_data['weight'] / 10} kg")
        embed.add_field(name='Abilities', value=', '.join([ability['ability']['name'] for ability in pokemon_data['abilities']]))
        embed.set_thumbnail(url=pokemon_data['sprites']['front_default'])

        # Send the embed
        await ctx.send(embed=embed)

    else:
        await ctx.send(embed=discord.Embed(description=f"Pokemon {pokemon_name.capitalize()} not found!",
                                           color=discord.Color.red()))

# Shop command
@bot.command(name='shop', help='View items available in the shop')
async def shop(ctx):
    # Create an embed with shop items
    embed = discord.Embed(title='Pokemart - Shop Items', color=discord.Color.gold(),
                          description='Welcome to the Pokemart! Here are the items available for purchase:')
    
    for item, price in shop_items.items():
        embed.add_field(name=f"{item} - {price} Poke Dollars", value="Buy with `l.buy [item]`", inline=False)
    
    # Set the thumbnail
    thumbnail_url = "https://th.bing.com/th/id/OIP.mxCrHbetATahntTghPb1jQEQDl?w=221&h=186&c=7&r=0&o=5&pid=1.7"
    embed.set_thumbnail(url=thumbnail_url)

    # Send the embed
    await ctx.send(embed=embed)

# Buy command
@bot.command(name='buy', help='Buy an item from the shop')
async def buy(ctx, item_name):
    item_name = item_name.lower().capitalize()
    if item_name in shop_items:
        price = shop_items[item_name]
        if user_coins[ctx.author.id] >= price:
            add_item(ctx.author.id, item_name)
            remove_coins(ctx.author.id, price)
            await ctx.send(f"Successfully bought {item_name} for {price} Poke Dollars!")
        else:
            await ctx.send("You don't have enough Poke Dollars to buy this item.")
    else:
        await ctx.send("Item not found in the shop.")

# Give coins command (for testing purposes)
@bot.command(name='give_coins', help='Give coins to a user')
async def give_coins(ctx, user: discord.User, amount: int):
    if ctx.author.id == 1046198375265083483:  # Replace YOUR_USER_ID with your own Discord user ID
        add_coins(user.id, amount)
        await ctx.send(f"Gave {amount} Poke Dollars to {user.name}.")
    else:
        await ctx.send("You don't have permission to use this command.")


@bot.command(name='help', help='Show this message')
async def help_command(ctx):
    # Create an embed with help information
    embed = discord.Embed(title='LakK Bot Help',
                          description=f"Prefix: {prefix}\n\n**Commands:**\n"
                                      f"- `catch` - Catch a random wild Pokemon using a Poke Ball\n"
                                      f"- `pokedex [pokemon_name]` - Get information about a Pokemon from the Pokedex\n"
                                      f"- `shop` - View items available in the shop\n"
                                      f"- `buy [item]` - Buy an item from the shop\n"
                                      f"- `help` - Show this message",
                          color=discord.Color.orange())


    await ctx.send(embed=embed)

import os
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
