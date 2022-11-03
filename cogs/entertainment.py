import discord
import random
import praw
import discord
from discord.commands import Option
import aiohttp
import os


reddit_id = os.environ['reddit_id']
reddit_secret = os.environ['reddit_secret']
reddit_user = os.environ['reddit_user']
reddit_pass = os.environ['reddit_pass']
token = os.environ['token']
waifuchoices = ['waifu', 'neko', 'shinobu', 'megumin', 'bully', 'cuddle', 'hug', 'awoo', 'pat', 'smug', 'bonk', 'yeet','blush', 'smile', 'wave', 'highfive', 'handhold', 'nom', 'bite', 'slap', 'happy', 'wink', 'dance','cringe']
subchoices = ['memes', 'cursedimages', 'dankmemes', 'cursedcomments', 'blessedimages', 'NoahGetTheBoat', 'aww', 'FoodPorn', 'TIHI', 'MapPorn', 'HolUp', 'softwaregore', 'awwnime', 'wholesomememes']


class EntertainmentCog(discord.Cog):
    """This cog holds the logic for working with entertainment commands"""
    def __init__(self, bot):
        self.bot = bot
        print(f"cog: {self.qualified_name} loaded")
        self.reddit_instance = praw.Reddit(client_id = reddit_id,
                      client_secret = reddit_secret,
                      username = reddit_user,
                      password= reddit_pass,
                      user_agent = "abghan", check_for_async=False)





    @discord.slash_command(name='urban',
    description="Gets a word's definition from Urban Dictionary")
    async def urban(self, ctx, word):
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


    @discord.slash_command(name='reddit',
        description="Sends a random image from a chosen subreddit")
    async def reddit(self, ctx, subred: Option(
        str, description="Choose your subreddit", choices=subchoices)):
        '''Sends a random image from a chosen subreddit'''
        subreddit = self.reddit_instance.subreddit(subred)
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


    @discord.slash_command(name='waifu', description='Sends a random anime girl picture')
    async def waifu(self, ctx, type: Option(str, description="Enter your preferred type", choices=waifuchoices)):
        '''anime girls pics'''
        async with aiohttp.ClientSession() as session:
            request = await session.get(f'https://api.waifu.pics/sfw/{type}')
            testjson = await request.json()
        embed = discord.Embed(title=f"{type}", color=discord.Color.random(), type='image')
        embed.set_image(url=testjson['url'])
        await ctx.respond(embed=embed)




def setup(bot):
    bot.add_cog(EntertainmentCog(bot))