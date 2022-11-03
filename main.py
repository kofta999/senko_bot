'''The main bot code'''
import os
import discord
from dotenv import load_dotenv

load_dotenv()

token = os.environ['token']

bot = discord.Bot()
bot.load_extensions('cogs')


@bot.event
async def on_ready():
    '''Actions done on ready'''
    await bot.change_presence(status=discord.Status.online,activity=discord.Activity(
            type=discord.ActivityType.watching, name="世話焼きキツネの仙狐さん"))
    print(f'We have logged in as {bot.user}')


# @bot.slash_command(description="Creates a reminder")
# async def reminder(ctx: discord.ApplicationContext, message: Option(str), seconds: Option(int)):
#     '''creates a reminder to the user's dm'''
#     await ctx.author.send(content=message)
#     await ctx.respond("Created the reminder")


# @tasks.loop(seconds=5)
# async def remind():
#     now = datetime.utcnow()
#     print(now)


@bot.event
async def on_message(message):
    '''loop check'''
    if message.author == bot.user:
        return


bot.run(token)
