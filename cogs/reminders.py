import discord
import motor.motor_asyncio
import os
from discord import NotFound
from discord.ext import tasks
from datetime import datetime
from discord.commands import Option
from dpytools.parsers import to_timedelta
from dotenv import load_dotenv

load_dotenv()

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["client_url"])
db = client.reminders


class ReminderCog(discord.Cog):
    """This cog holds the logic for working with reminders"""

    def __init__(self, bot):
        self.bot = bot
        self.remind.start()
        print(f"cog: {self.qualified_name} loaded")

    @discord.slash_command(description="Creates a reminder")
    async def reminder(self, ctx, message: Option(str), time: Option(str)):
        '''creates a reminder and sends it to the user's dm'''

        time = to_timedelta(time)
        now = datetime.utcnow()
        when = now + time

        await db.all_reminders.insert_one({
            'user_id': ctx.author.id,
            'next_time': when,
            'content': message,
            'done': False,
        })

        await ctx.respond(f"Created the reminder on {when.strftime('%x %X')} (utc)")

    @discord.slash_command(description="Shows all reminders that you've created")
    async def all_reminders(self, ctx):
        '''shows all reminders for a user'''
        s = ''
        reminders = db.all_reminders.find({'done': False, 'user_id': ctx.author.id})
        if not reminders:
            await ctx.repsond("There's no current reminders")
        async for reminder in reminders:
            s += f"A reminder on {reminder['next_time'].strftime('%x %X')} (utc) with the content:\n{reminder['content']}"
        await ctx.respond(s)


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