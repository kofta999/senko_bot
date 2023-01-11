"""This cog holds the logic for working with reminders"""

from datetime import datetime
import discord
import motor.motor_asyncio
import os
from discord import NotFound
from discord.ext import tasks
from discord.commands import Option
from dpytools.parsers import to_timedelta
from dotenv import load_dotenv
import logging


load_dotenv()

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["client_url"])
db = client.reminders


class ReminderCog(discord.Cog):
    """This class holds the logic for working with reminders"""

    def __init__(self, bot):
        self.bot = bot
        self.remind.start()
        print(f"cog: {self.qualified_name} loaded")

    @discord.slash_command(description="Creates a reminder")
    async def reminder(self, ctx, message: Option(str), time: Option(str)):
        '''creates a reminder and sends it to the user's dm'''

        try:
            time = to_timedelta(time)
            now = datetime.utcnow()
            when = now + time
        except Exception:
            await ctx.respond("Enter a valid time in format <number>[s|m|h|d|w]")

        await db.all_reminders.insert_one({
            'user_id': ctx.author.id,
            'next_time': when,
            'content': message,
            'done': False,
        })

        embed = discord.Embed(color=discord.Color.orange(), type='rich')
        embed.add_field(name='\u200b', value=f"Created the reminder on {when.strftime('%x %X')} (UTC)", inline=False)
        await ctx.respond(embed=embed)

    @discord.slash_command(description="Shows all reminders that you've created")
    async def all_reminders(self, ctx):
        '''shows all reminders for a user'''
        logging.info("beginning of the command")
        embed = discord.Embed(color=discord.Color.orange(), type='rich')
        reminders = db.all_reminders.find({'done': False, 'user_id': ctx.author.id})
        logging.info("Got all reminders")

        async for reminder in reminders:
            logging.info("in try")
            embed.add_field(name="\u200b", value=f"• A reminder on {reminder['next_time'].strftime('%x %X')} (UTC) with the content: **{reminder['content']}**", inline=False)

        try:
            await ctx.respond(embed=embed)
        except discord.errors.HTTPException:
            await ctx.respond(f"There's no current reminders for {ctx.author}")


    @tasks.loop(seconds=5)
    async def remind(self):
        await self.bot.wait_until_ready()
        now = datetime.utcnow()
        reminders = db.all_reminders.find({'done': False, 'next_time': {'$lte': now}})
        async for reminder in reminders:
            try:
                user =  await self.bot.fetch_user(reminder['user_id'])

            except NotFound:
                if reminder['next_time'] <= (now - to_timedelta(days=2)):
                    reminder['done'] = True
                    await db.all_reminders.replace_one({'_id': reminder['_id']}, reminder)
                    await db.all_reminders.delete_one({'done': True, '_id': reminder['_id']})
                    continue
            else:
                if user:
                    await user.send(reminder['content'])
                    reminder['done'] = True
                    await db.all_reminders.replace_one({'_id': reminder['_id']}, reminder)
                    await db.all_reminders.delete_one({'done': True, '_id': reminder['_id']})




def setup(bot):
    bot.add_cog(ReminderCog(bot))