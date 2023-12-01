import discord
from discord import app_commands 
from discord.ext import commands
import psutil
import datetime
from discord import ui

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="?", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} - {bot.user.id}")
    await bot.tree.sync()

@bot.tree.command(name="help")
async def help_menu(interaction: discord.Interaction):
    embeds = []
    
    # Create embed for each cog
    info = discord.Embed(title="Info")
    info.add_field(name="/serverinfo", value="Shows server information")
    info.add_field(name="/userinfo", value="Shows user information")
    embeds.append(info)
    
    mod = discord.Embed(title="Moderation") 
    mod.add_field(name="/purge", value="Purges messages")
    mod.add_field(name="/kick", value="Kicks a member")
    mod.add_field(name="/ban", value="Bans a member")
    embeds.append(mod)
    
    # Send embeds paginated
    pages = discord.ui.View() 
    pages.add_item(discord.ui.Button(label="Prev"))
    pages.add_item(discord.ui.Button(label="Next"))
    
    await interaction.response.send_message(embed=embeds[0], view=pages, ephemeral=True)

@bot.tree.command()
async def serverinfo(interaction: discord.Interaction):
    emb = discord.Embed(timestamp=datetime.datetime.utcnow())
    
    emb.set_author(name=interaction.guild.name, icon_url=interaction.guild.icon.url)
    emb.add_field(name="Members", value=interaction.guild.member_count) 
    # other fields
    
    await interaction.response.send_message(embed=emb)
    
@bot.tree.command()  
async def userinfo(interaction: discord.Interaction, member: discord.Member):
    roles = [role.mention for role in member.roles[1:]] # exclude @everyone
    
    embed = discord.Embed(timestamp=datetime.utcnow())
    embed.set_author(name=str(member), icon_url=member.avatar.url)
    embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Joined At", value=member.joined_at.strftime("%#d %B %Y, %I:%M %p UTC"))
    embed.add_field(name="Account Created", value=member.created_at.strftime("%#d %B %Y, %I:%M %p UTC"))
    embed.add_field(name=f"Roles [{len(roles)}]", value=" ".join(roles), inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command()
async def system(interaction: discord.Interaction):
    embed = discord.Embed(title="System Information")
    
    cpu_use = psutil.cpu_percent()
    ram_use = psutil.virtual_memory().percent
    disk_use = psutil.disk_usage('/').percent
    
    embed.add_field(name="CPU Usage", value=f"{cpu_use}%") 
    embed.add_field(name="RAM Usage", value=f"{ram_use}%")
    embed.add_field(name="Disk Usage", value=f"{disk_use}%")
    
    await interaction.response.send_message(embed=embed) 
    
@bot.command()
async def purge(ctx, amount):
    await ctx.channel.purge(limit=amount)
    
@bot.command()    
async def kick(ctx, member : discord.Member): 
    await member.kick()
    
@bot.command()   
async def ban(ctx, member : discord.Member):
    await member.ban()
    
import os
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)

