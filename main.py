'''The main bot code'''
from datetime import timedelta
import random
import json
import os
import praw
import discord
from discord.commands import Option
from dotenv import load_dotenv
import aiohttp
from keep_alive import keep_alive

load_dotenv()

reddit_id = os.environ['reddit_id']
reddit_secret = os.environ['reddit_secret']
reddit_user = os.environ['reddit_user']
reddit_pass = os.environ['reddit_pass']
token = os.environ['token']
waifuchoices = ['waifu', 'neko', 'shinobu', 'megumin', 'bully', 'cuddle', 'hug', 'awoo', 'pat', 'smug', 'bonk', 'yeet','blush', 'smile', 'wave', 'highfive', 'handhold', 'nom', 'bite', 'slap', 'happy', 'wink', 'dance','cringe']
subchoices = ['memes', 'cursedimages', 'dankmemes', 'cursedcomments', 'blessedimages', 'NoahGetTheBoat', 'aww', 'FoodPorn', 'TIHI', 'MapPorn', 'HolUp', 'softwaregore', 'awwnime', 'wholesomememes']

bot = discord.Bot()

# reddit app
reddit_instance = praw.Reddit(client_id = reddit_id,
                      client_secret = reddit_secret,
                      username = reddit_user,
                      password= reddit_pass,
                      user_agent = "abghan", check_for_async=False)


@bot.event
async def on_ready():
    '''Actions done on ready'''
    await bot.change_presence(status=discord.Status.online,activity=discord.Activity(
            type=discord.ActivityType.watching, name="世話焼きキツネの仙狐さん"))
    print(f'We have logged in as {bot.user}')


# help command
@bot.slash_command(name='help', description="get list of avillable commands")
async def helpjson(ctx):
    '''help menu'''
    with open('help.json', 'r', encoding='UTF-8') as help_file:
        help_commands = json.load(help_file)
        help_embed = discord.Embed.from_dict(help_commands)
        await ctx.respond(embed=help_embed)


#urban dictionary command
@bot.slash_command(name='urban',
    description="Gets a word's definition from Urban Dictionary")
async def urban(ctx, word):
    '''urban dictionary command'''
    async with aiohttp.ClientSession() as session:
        request = await session.get(f'http://api.urbandictionary.com/v0/define?term={word}')
        testjson = await request.json()
    embed = discord.Embed(title=f"{word}", color=discord.Color.blue(), type='rich')
    firstdef = testjson["list"][0]
    embed.add_field(name='Definition', value=firstdef['definition'])
    embed.add_field(name='Example', value=firstdef['example'])
    embed.set_author(name="Defenation of ")
    embed.set_footer(text=f"By {firstdef['author']}")
    await ctx.respond(embed=embed)


#reddit command
@bot.slash_command(name='reddit',
    description="Sends a random image from a chosen subreddit")
async def reddit(ctx, subred: Option(
    str, description="Choose your subreddit", choices=subchoices)):
    '''Sends a random image from a chosen subreddit'''
    subreddit = reddit_instance.subreddit(subred)
    subs = []
    hot = subreddit.hot(limit=50)
    for sub in hot:
        subs.append(sub)
    random_sub = random.choice(subs)
    name = random_sub.title
    url = random_sub.url
    embed = discord.Embed(type='rich', title=name, color=discord.Color.orange())
    embed.set_image(url=url)
    await ctx.respond(embed=embed)


#clear masseges
@bot.slash_command(
    description="Deletes a specefic amount of messages")
async def clear(ctx, amount: Option(
    int, "Amount of messages you want to delete", default=1)):
    '''Deletes a specefic amount of messages'''
    if ctx.author.guild_permissions.manage_messages:
        await ctx.channel.purge(limit=amount)
        await ctx.respond("Done")
    else:
        await ctx.respond("You don't have enough permissions")


#anime girls api
@bot.slash_command(name='waifu', description='Sends a random anime girl picture')
async def waifu(ctx, type: Option(str, description="Enter your preferred type", choices=waifuchoices)):
    '''anime girls pics'''
    async with aiohttp.ClientSession() as session:
        request = await session.get(f'https://api.waifu.pics/sfw/{type}')
        testjson = await request.json()
    embed = discord.Embed(title=f"{type}", color=discord.Color.random(), type='image')
    embed.set_image(url=testjson['url'])
    await ctx.respond(embed=embed)


#change bot name
@bot.slash_command(description="Changes the bot's name")
async def rename(ctx, name):
    '''bot name changer'''
    await bot.user.edit(username=name)
    await ctx.respond(f"bot usernaem was changed to {name}")


@bot.event
async def on_message(message):
    '''loop check'''
    if message.author == bot.user:
        return


keep_alive()
bot.run(token)
