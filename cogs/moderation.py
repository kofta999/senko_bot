import discord
import json
from discord.commands import Option

class ModerationCog(discord.Cog):

    def __init__(self, bot):
        self.bot = bot
        print(f"cog: {self.qualified_name} loaded")


    @discord.slash_command(name='help', description="get list of avaliable commands")
    async def helpjson(self, ctx):
        '''help menu'''
        with open('help.json', 'r', encoding='UTF-8') as help_file:
            help_commands = json.load(help_file)
            help_embed = discord.Embed.from_dict(help_commands)
            await ctx.respond(embed=help_embed)


    @discord.slash_command(
        description="Deletes a specefic amount of messages")
    async def clear(self, ctx, amount: Option(
        int, "Amount of messages you want to delete", default=1)):
        '''Deletes a specefic amount of messages'''
        if ctx.author.guild_permissions.manage_messages:
            await ctx.channel.purge(limit=amount)
            await ctx.respond("Done")
        else:
            await ctx.respond("You don't have enough permissions")


    @discord.slash_command(description="Changes the bot's name")
    async def rename(self, ctx, name):
        '''bot name changer'''
        await discord.user.edit(username=name)
        await ctx.respond(f"bot usernaem was changed to {name}")


def setup(bot):
    bot.add_cog(ModerationCog(bot))