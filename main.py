import disnake
from disnake.ext import commands
from disnake.ui import View, button
import requests
import random

bot = commands.Bot(command_prefix='/')

# Define some constants
POKEAPI_BASE_URL = 'https://pokeapi.co/api/v2/'
MAX_POKEMON_CAPACITY = 100

# User storage (replace this with a proper database)
user_pokemon = {}

# /catch command
@bot.slash_command(name="catch", description="Catch a Pokémon")
async def _catch(ctx):
    pokemon_name = get_random_pokemon()
    embed = disnake.Embed(title=f"You caught a wild {pokemon_name}!", color=disnake.Color.green())
    await ctx.send(embed=embed)

    # Add the caught Pokémon to the user's storage
    user_id = str(ctx.author.id)
    if user_id not in user_pokemon:
        user_pokemon[user_id] = []
    user_pokemon[user_id].append(pokemon_name)

# /pokedex command
@bot.slash_command(name="pokedex", description="View your Pokémon")
async def _pokedex(ctx):
    user_id = str(ctx.author.id)
    if user_id not in user_pokemon or not user_pokemon[user_id]:
        await ctx.send("Your Pokédex is empty!")
        return

    pokedex_pages = [create_pokedex_embed(page + 1, user_pokemon[user_id][page * 10 : (page + 1) * 10]) for page in range((len(user_pokemon[user_id]) - 1) // 10 + 1)]
    view = PokedexView(pokedex_pages)
    await ctx.send(embed=pokedex_pages[0], view=view)

class PokedexView(View):
    def __init__(self, pages):
        super().__init__()
        self.pages = pages

    @button(label="Prev", style=disnake.ButtonStyle.gray)
    async def prev_button(self, button, interaction):
        await self.show_page(interaction, -1)

    @button(label="Next", style=disnake.ButtonStyle.gray)
    async def next_button(self, button, interaction):
        await self.show_page(interaction, 1)

    async def show_page(self, interaction, direction):
        current_page = self.current_page(interaction)
        new_page = (current_page + direction) % len(self.pages)
        await interaction.message.edit(embed=self.pages[new_page], view=self)

    def current_page(self, interaction):
        return self.pages.index(interaction.message.embeds[0])

# /release command
@bot.slash_command(name="release", description="Release a Pokémon")
async def _release(ctx, pokemon_name: str):
    user_id = str(ctx.author.id)
    if user_id not in user_pokemon or pokemon_name not in user_pokemon[user_id]:
        await ctx.send("You don't have that Pokémon!")
        return

    user_pokemon[user_id].remove(pokemon_name)
    await ctx.send(f"You released {pokemon_name}!")

# /start command
@bot.slash_command(name="start", description="Register as a trainer")
async def _start(ctx):
    view = StartView()
    await ctx.send("Welcome to the world of Pokémon! What is your trainer name?", view=view)

class StartView(View):
    def __init__(self):
        super().__init__()

    @button(label="Register", style=disnake.ButtonStyle.green)
    async def register_button(self, button, interaction):
        await interaction.response.send_message("Trainer registration complete!", ephemeral=True)
        await self.clear_buttons()

# /trade command
@bot.slash_command(name="trade", description="Trade Pokémon with another user")
async def _trade(ctx, other_user: disnake.User):
    await ctx.send(f"Initiating trade with {other_user.name}!")

# /shop command
@bot.slash_command(name="shop", description="Visit the Pokémon shop")
async def _shop(ctx):
    shop_items = get_shop_items()
    embed = create_shop_embed(shop_items)
    await ctx.send(embed=embed)

def get_random_pokemon():
    # Fetch a random Pokémon from the PokeAPI
    response = requests.get(f"{POKEAPI_BASE_URL}pokemon/{random.randint(1, 898)}")
    data = response.json()
    return data['name'].capitalize()

def create_pokedex_embed(page_number, pokemon_list):
    embed = disnake.Embed(title=f"Your Pokédex - Page {page_number}", color=disnake.Color.blue())
    for pokemon in pokemon_list:
        embed.add_field(name=pokemon, value="Owned", inline=True)
    return embed

async def get_shop_items():
    # Fetch items from the PokeAPI
    response = await fetch_pokeapi_data('item?limit=30')  # Adjust the limit as needed
    items = response['results']
    
    shop_items = []
    for item in items:
        item_data = await fetch_pokeapi_data(item['url'])
        shop_items.append({
            'name': item_data['name'].capitalize(),
            'description': item_data['effect_entries'][0]['effect'],
            'price': 100  # Set a default price, adjust as needed
        })

    return shop_items

def create_shop_embed(shop_items):
    embed = disnake.Embed(title="Pokémon Shop", color=disnake.Color.gold())

    for item in shop_items:
        embed.add_field(
            name=f"{item['name']} - {item['price']} Poké Dollars",
            value=f"Description: {item['description']}",
            inline=False
        )

    return embed

async def fetch_pokeapi_data(endpoint):
    # Fetch data from the PokeAPI
    response = await bot.http.get(f"{POKEAPI_BASE_URL}{endpoint}")
    data = response.json()
    return data

import os
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
