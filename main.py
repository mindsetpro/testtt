import discord
from discord.ext import commands
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

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

# Catch command
@bot.command(name='catch', help='Catch a wild Pokemon!')
async def catch(ctx, pokemon_name):
    # Get Pokemon data from PokeAPI
    response = requests.get(pokeapi_base_url + pokemon_name.lower())
    if response.status_code == 200:
        pokemon_data = response.json()

        # Generate a random chance for shiny or escape
        shiny_chance = random.randint(1, 10)
        escape_chance = random.randint(1, 10)

        # Create an embed with Pokemon information
        embed = discord.Embed(title=f"Wild {pokemon_name.capitalize()} appeared!",
                              description=f"Shiny Chance: {shiny_chance}/10\nEscape Chance: {escape_chance}/10",
                              color=discord.Color.blue())
        embed.set_thumbnail(url=pokemon_data['sprites']['front_default'])

        # Check if the Pokemon is shiny or escaped
        if shiny_chance == 1:
            embed.add_field(name='Result', value="Congratulations! You caught a shiny Pokemon!")
        elif escape_chance == 1:
            embed.add_field(name='Result', value=f"Oh no! {pokemon_name.capitalize()} escaped!")
        else:
            embed.add_field(name='Result', value=f"You caught {pokemon_name.capitalize()}!")

        # Send the embed
        await ctx.send(embed=embed)

    else:
        await ctx.send(embed=discord.Embed(description=f"Pokemon {pokemon_name.capitalize()} not found!",
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


# Help command
@bot.command(name='help', help='Show this message')
async def help_command(ctx):
    # Create an embed with help information
    embed = discord.Embed(title='Pokemon RPG Bot Help',
                          description=f"Prefix: {prefix}\n\n**Commands:**\n"
                                      f"- {prefix}catch [pokemon_name]\n"
                                      f"- {prefix}pokedex [pokemon_name]\n"
                                      f"- {prefix}shop\n"
                                      f"- {prefix}help",
                          color=discord.Color.orange())

    # Send the embed
    await ctx.send(embed=embed)

        
import os
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
