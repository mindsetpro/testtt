import discord
from discord.ext import commands
from discord.ui import Button
import httpx  # Import httpx instead of requests

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="c?", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

@bot.command(name="catch")
async def catch(ctx):
    try:
        # Generate a random Pokemon ID between 1 and 1016
        random_pokemon_id = random.randint(1, 1016)

        # Fetch Pokemon data from PokeAPI
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{random_pokemon_id}")
            pokemon_data = response.json()

        # Fetch official Pokemon art URL from PokeAPI
        official_art_url = f"https://pokeapi.co/media/sprites/pokemon/other/official-artwork/{random_pokemon_id}.png"

        # Create an embed with Pokemon information
        embed = discord.Embed(title=f"Info about Pokemon #{random_pokemon_id}",
                              description=f"Type: {', '.join([t['type']['name'] for t in pokemon_data['types']])}",
                              color=discord.Color.blue())

        embed.set_image(url=official_art_url)

        await ctx.send(embed=embed)

    except Exception as e:
        print(e)
        await ctx.send("Error fetching Pokemon data!")

class PokedexView(discord.ui.View):
    def __init__(self, pokedex_data):
        super().__init__()
        self.pokedex_data = pokedex_data

    async def on_timeout(self):
        await self.message.edit(view=None)

    async def on_button_click(self, button, interaction):
        index = int(button.custom_id)
        pokemon_info = self.pokedex_data[index]

        embed = discord.Embed(title=pokemon_info['name'].capitalize(), color=discord.Color.green())
        embed.set_image(url=f"https://pokeres.bastionbot.org/images/pokemon/{index + 1}.png")

        await interaction.response.edit_message(embed=embed, view=self)

@bot.command(name="pokedex")
async def pokedex(ctx):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://pokeapi.co/api/v2/pokemon?limit=151")
            pokedex_data = response.json()['results']

        pokedex_view = PokedexView(pokedex_data)

        embed = discord.Embed(title="Pokedex", color=discord.Color.blue())
        embed.set_image(url="https://i.imgur.com/nP1l06D.png")

        pokedex_view.message = await ctx.send(embed=embed, view=pokedex_view)

        for index, pokemon_info in enumerate(pokedex_data):
            button = Button(style=discord.ButtonStyle.grey, label=pokemon_info['name'].capitalize(), custom_id=str(index))
            pokedex_view.add_item(button)

    except Exception as e:
        print(e)
        await ctx.send("Error fetching Pokedex data!")

@bot.command(name="shop")
async def shop(ctx):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://pokeapi.co/api/v2/item?limit=10")
            shop_items = response.json()['results']

        for shop_item in shop_items:
            embed = discord.Embed(title=shop_item['name'].capitalize(), color=discord.Color.purple())
            await ctx.send(embed=embed)

    except Exception as e:
        print(e)
        await ctx.send("Error fetching shop data!")


import os
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)

