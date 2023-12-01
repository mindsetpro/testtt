import discord
from discord.ext import commands
import random 
import requests
from PIL import Image, ImageDraw, ImageFont 

subreddit = 'FightVids'

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="?", intents=intents)

users = {} 

@bot.event
async def on_message(message):
    if message.author not in users:
        users[message.author] = {}
        users[message.author]['xp'] = 0  
        users[message.author]['level'] = 1

    users[message.author]['xp'] += random.randint(15, 25)

    if users[message.author]['xp'] >= 100 * (users[message.author]['level']): 
        users[message.author]['level'] += 1
        await message.channel.send(f"**{message.author.name} has leveled up to level {users[message.author]['level']}!**")

    await bot.process_commands(message)

@bot.command()
async def rank(ctx):   
    xp = users[ctx.author]['xp']
    lvl = users[ctx.author]['level']
    xp_for_nxt_lvl = 100 * lvl
    
    percentage = int(100 * xp / xp_for_nxt_lvl)  
    
    # Creates progress bar
    img = Image.new('RGB', (400, 40), color=(73, 109, 137)) 
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, percentage * 4, 40), fill=(255, 0, 0)) 
    fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 20)
    d.text((200, 10), str(percentage)+'%', font=fnt, fill=(255,255,0))
    
    img.save('progress.png')
    
    embed = discord.Embed(title=f"{ctx.author.name}'s Rank")
    file = discord.File("progress.png", filename="image.png")
    embed.set_image(url="attachment://image.png")
    embed.add_field(name="Level", value=lvl)
    embed.add_field(name="XP", value=f"{xp}/{xp_for_nxt_lvl}")
    
    await ctx.send(file=file, embed=embed)
    
@bot.command() 
async def fight(ctx):
    response = requests.get(f'https://www.reddit.com/r/{subreddit}/random/.json')
    data = response.json()
    permalink = data[0]['data']['children'][0]['data']['permalink']
    link = f'https://www.reddit.com{permalink}'
    await ctx.send(link)
    
import os
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)

