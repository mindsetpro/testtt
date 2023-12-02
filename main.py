import discord
from discord.ext import commands, tasks
import random
import sqlite3
import requests
from PIL import Image, ImageDraw, ImageFont
import os

subreddit = 'FightVids'

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="?", intents=intents)

# Initialize SQLite database
conn = sqlite3.connect('your_database.db')  # Replace 'your_database.db' with your actual database name
cursor = conn.cursor()

# Create users table if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT,
        xp INTEGER,
        level INTEGER
    )
''')
conn.commit()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    update_leaderboard.start()

@tasks.loop(minutes=10)  # Update leaderboard every 10 minutes
async def update_leaderboard():
    cursor.execute('SELECT * FROM users ORDER BY xp DESC LIMIT 10')
    users = cursor.fetchall()

    # Create a leaderboard embed
    leaderboard_embed = discord.Embed(title="Leaderboard", color=discord.Color.gold())
    for index, user in enumerate(users, start=1):
        leaderboard_embed.add_field(name=f"{index}. {user[1]}", value=f"Level: {user[3]} | XP: {user[2]}", inline=False)

    # Get the server's leaderboard channel (replace with your actual channel ID)
    leaderboard_channel = bot.get_channel(123456789012345678)
    await leaderboard_channel.send(embed=leaderboard_embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore messages from bots

    # Check if the user exists in the database, if not, add them
    cursor.execute('SELECT * FROM users WHERE user_id=?', (str(message.author.id),))
    user_data = cursor.fetchone()
    if not user_data:
        cursor.execute('INSERT INTO users VALUES (?, ?, ?, ?)', (str(message.author.id), message.author.name, 0, 1))
        conn.commit()

    # Increment user's XP
    cursor.execute('UPDATE users SET xp = xp + ? WHERE user_id = ?', (random.randint(15, 25), str(message.author.id)))
    conn.commit()

    # Check for level-up
    cursor.execute('SELECT * FROM users WHERE user_id=?', (str(message.author.id),))
    user_data = cursor.fetchone()
    if user_data[2] >= 100 * user_data[3]:
        cursor.execute('UPDATE users SET level = level + 1 WHERE user_id = ?', (str(message.author.id),))
        conn.commit()
        await message.channel.send(f"**{message.author.name} has leveled up to level {user_data[3]}!**")

    await bot.process_commands(message)

@bot.command()
async def rank(ctx):
    cursor.execute('SELECT * FROM users WHERE user_id=?', (str(ctx.author.id),))
    user_data = cursor.fetchone()
    xp = user_data[2]
    lvl = user_data[3]
    xp_for_nxt_lvl = 100 * lvl
    percentage = int(100 * xp / xp_for_nxt_lvl)

    # Creates progress bar
    img = Image.new('RGB', (400, 40), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, percentage * 4, 40), fill=(255, 0, 0))
    fnt = ImageFont.load_default()
    d.text((200, 10), str(percentage) + '%', font=fnt, fill=(255, 255, 0))

    img.save('progress.png')

    # Create rank embed
    embed = discord.Embed(title=f"{ctx.author.name}'s Rank")
    file = discord.File("progress.png", filename="image.png")
    embed.set_image(url="attachment://image.png")
    embed.add_field(name="Level", value=lvl)
    embed.add_field(name="XP", value=f"{xp}/{xp_for_nxt_lvl}")

    await ctx.send(file=file, embed=embed)

@bot.command()
async def leaderboard(ctx):
    cursor.execute('SELECT * FROM users ORDER BY xp DESC LIMIT 10')
    users = cursor.fetchall()

    # Create a leaderboard embed
    leaderboard_embed = discord.Embed(title="Leaderboard", color=discord.Color.gold())
    for index, user in enumerate(users, start=1):
        leaderboard_embed.add_field(name=f"{index}. {user[1]}", value=f"Level: {user[3]} | XP: {user[2]}", inline=False)

    await ctx.send(embed=leaderboard_embed)

@bot.command()
async def serverinfo(ctx):
    # Create a server info embed
    server_embed = discord.Embed(title=f"{ctx.guild.name} Server Information", color=discord.Color.blue())
    server_embed.set_thumbnail(url=ctx.guild.icon_url)
    server_embed.add_field(name="Owner", value=ctx.guild.owner, inline=True)
    server_embed.add_field(name="Members", value=ctx.guild.member_count, inline=True)
    server_embed.add_field(name="Region", value=ctx.guild.region, inline=True)
    server_embed.add_field(name="Created At", value=ctx.guild.created_at.strftime("%B %d, %Y"), inline=True)

    await ctx.send(embed=server_embed)

@bot.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"{member.name} has been banned for {reason}.")

@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f"{member.name} has been kicked for {reason}.")

@bot.event
async def on_guild_channel_create(channel):
    # Check if the created channel is the target channel for random fight videos
    if channel.id == 1180258553227903137:
        await send_random_fight_video(channel)

async def send_random_fight_video(channel):
    # Use Reddit API to get a random fight video from the specified subreddit
    reddit_url = f'https://www.reddit.com/r/{subreddit}/random.json'
    response = requests.get(reddit_url, headers={'User-agent': 'Mozilla/5.0'})

    if response.status_code == 200:
        data = response.json()
        video_url = data[0]['data']['children'][0]['data']['url']
        await channel.send(f"Check out this real fight video: {video_url}")

    
import os
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)

