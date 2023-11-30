import disnake
from disnake.ext import commands, tasks
import asyncio
import time
import random

intents = disnake.Intents.all()  # Enable all intents
bot = commands.Bot(command_prefix='/', intents=intents)

# Dictionary to store active giveaways
giveaways = {}
giveaway_start_times = {}
giveaway_channels = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@tasks.loop(seconds=60)  # Check every minute
async def check_giveaways():
    for giveaway_data in giveaways.values():
        duration, message_id = giveaway_data
        remaining_time = duration - (time := int(time.time() - giveaway_start_times[message_id]))

        if remaining_time <= 0:
            # Giveaway has ended
            await end_giveaway(message_id)
        else:
            # Update the remaining time in the message
            message = await bot.get_channel(giveaway_channels[message_id]).fetch_message(message_id)
            embed = message.embeds[0]
            embed.description = f"React with 🎉 to enter!\nTime remaining: {remaining_time // 60} minutes"
            await message.edit(embed=embed)

async def end_giveaway(message_id):
    # Your giveaway ending logic here
    # For example, pick a winner randomly
    message = await bot.get_channel(giveaway_channels[message_id]).fetch_message(message_id)
    reactions = [reaction for reaction in message.reactions if str(reaction.emoji) == '🎉']
    winner = None

    if reactions:
        winner = reactions[0].users().filter(lambda u: not u.bot).random()

    # Announce the winner
    if winner:
        winner_mention = winner.mention
    else:
        winner_mention = "No one entered the giveaway. 😢"

    embed = disnake.Embed(
        title=f"🏆 Giveaway Winner 🏆",
        description=f"Congratulations {winner_mention}! You won the giveaway!",
        color=0x2ecc71  # Green color for the winner
    )
    await bot.get_channel(giveaway_channels[message_id]).send(embed=embed)

    # Stop the loop for this giveaway
    check_giveaways.stop()
    del giveaways[message_id]
    del giveaway_start_times[message_id]
    del giveaway_channels[message_id]

@bot.slash_command()
async def gw(ctx, duration: int):
    # Set up the giveaway details
    prize = "3000 EXP"
    image_url = "https://media.discordapp.net/attachments/1178407310033440818/1179785550471893073/image_16.png?ex=657b0bea&is=656896ea&hm=8ee74c54d0493ba27ad38379cbee9be31cdd77cb024fba65de6b3deec19f67de&=&format=webp&quality=lossless"

    # Create the giveaway embed
    embed = disnake.Embed(
        title=f"🎉 Giveaway: {prize} 🎉",
        description=f"React with 🎉 to enter!\nTime remaining: {duration} seconds",
        color=0x3498db  # Use any color you prefer
    )
    embed.set_image(url=image_url)
    embed.set_footer(text=f"Hosted by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)

    # Send the giveaway message
    giveaway_message = await ctx.send(embed=embed)
    await giveaway_message.add_reaction('🎉')  # Add reaction for entering the giveaway

    # Save giveaway data for later reference
    giveaways[giveaway_message.id] = (duration, giveaway_message.id)
    giveaway_start_times[giveaway_message.id] = int(time.time())
    giveaway_channels[giveaway_message.id] = ctx.channel.id

    # Add the reaction to the message
    await giveaway_message.add_reaction('🎉')

    # Start the loop to check for the giveaway end
    if not check_giveaways.is_running():
        check_giveaways.start()


@bot.slash_command()
async def reroll(ctx, message_id: int):
    if message_id in giveaways:
        # Reroll the giveaway
        await end_giveaway(message_id)
        await ctx.send(f"Rerolled the giveaway with message ID {message_id}.")
    else:
        await ctx.send(f"No active giveaway found with message ID {message_id}.")
import os
TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)
