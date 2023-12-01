import discord
from discord.ext import commands 
import random
import requests
from PIL import Image, ImageDraw, ImageFont

subreddit = 'fightporn' 

bot = commands.Bot(command_prefix='/')

@bot.command() 
async def rank(ctx):
    xp_current = 820  
    xp_to_level_up = 900
    
    percentage = int(100 * xp_current / xp_to_level_up)
    
    img = Image.new('RGB', (400, 40), color = (73, 109, 137))
    
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, percentage * 4, 40), fill=(255, 0, 0))
    
    fnt = ImageFont.truetype('Pillow/Tests/fonts/FreeMono.ttf', 20)
    d.text((200, 10), str(percentage)+'%', font=fnt, fill=(255,255,0))
    
    img.save('progress.png')
    
    embed = discord.Embed(title=f"{ctx.author.name}'s Rank")
    file = discord.File("progress.png", filename="image.png")
    embed.set_image(url="attachment://image.png")
    embed.add_field(name="Level", value="5") 
    embed.add_field(name="XP", value=f"{xp_current}/{xp_to_level_up}")  
    
    await ctx.send(file=file, embed=embed)

@bot.command()
async def fight(ctx):
    response = requests.get(f'https://reddit.com/r/{subreddit}/random.json')
    data = response.json()
    permalink = data[0]['data']['children'][0]['data']['permalink']
    link = f'https://reddit.com{permalink}'
    await ctx.send(link)
    
import os
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)

