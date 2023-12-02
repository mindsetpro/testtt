import discord
from discord.ext import commands
import requests
import random

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="--", intents=intents)

previous_videos = []

@bot.command() 
async def fight(ctx):

    for x in range(5):
        
        response = requests.get("https://t.me/s/onlyfighting/random")
        webpage = response.text
        
        while True:
            start_index = webpage.find('"src":"https://')
            if start_index == -1:
                break 
                
            end_index = webpage.find('"\\/', start_index + 10)
            video_url = webpage[start_index+8 : end_index]
            
            if video_url not in previous_videos:
                previous_videos.append(video_url)
                await ctx.send(f"https:{video_url}")
                break
                
import os
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)

