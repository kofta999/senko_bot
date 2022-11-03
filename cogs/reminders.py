import discord
from discord import NotFound
from discord.ext import tasks
from datetime import datetime
from discord.commands import Option
from dpytools.parsers import to_timedelta
import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb+srv://kofta:kokoko555@senko-cluster.6prehi1.mongodb.net/?retryWrites=true&w=majority")

db = client.reminders


class ReminderCog(discord.Cog):
    """This cog holds the logic for working with reminders"""

    def __init__(self, bot):
        self.bot = bot
        self.remind.start()
        print(f"cog: {self.qualified_name} loaded")

    @discord.slash_command(description="Creates a reminder")
    async def reminder(self, ctx, message: Option(str), time: Option(str)):
        '''creates a reminder to the user's dm'''

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
                    continue
            else:
                if user:
                    await user.send(reminder['content'])
                    reminder['done'] = True
                    await db.all_reminders.replace_one({'_id': reminder['_id']}, reminder)




def setup(bot):
    bot.add_cog(ReminderCog(bot))