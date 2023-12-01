import discord
import requests

subreddit = 'fightvideos'
limit = 10 

bot = discord.Bot()

@bot.event 
async def on_ready():
    channel = bot.get_channel(1055753999644635146)
    
    after = None
    while True:
        url = f'https://www.reddit.com/r/{subreddit}/hot.json'
        params = {'limit': limit, 'after': after}
        res = requests.get(url, params=params)
        data = res.json()
        
        for post in data['data']['children']:
            media = post['data']['secure_media']
            if media and 'reddit_video' in media:
                vid_url = media['reddit_video']['fallback_url']
                await channel.send(vid_url)
                
        after = data['data']['after']
        if not after:
            break

import os
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)

