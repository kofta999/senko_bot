'''The main bot code'''
import os
import discord
from dotenv import load_dotenv

load_dotenv()

token = os.environ['token']

bot = discord.Bot()
bot.load_extension('cogs.reminders')


@bot.event
async def on_ready():
    '''Actions done on ready'''
    await bot.change_presence(status=discord.Status.online,activity=discord.Activity(
            type=discord.ActivityType.watching, name="世話焼きキツネの仙狐さん"))
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_message(message):
    '''loop check'''
    if message.author == bot.user:
        return


bot.run(token)
