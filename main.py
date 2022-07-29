import discord, aiohttp, praw,random,json
from caesarcipher import CaesarCipher
from discord.commands import Option
from discord.ext import commands
from discord.ext.commands import MissingPermissions
from datetime import timedelta
from keep_alive import keep_alive
from not_main import serverids, waifuchoices, subchoices, token,reddit_id, reddit_secret, reddit_pass, reddit_user
bot = discord.Bot()

# reddit app
redditt = praw.Reddit(client_id = reddit_id,
                      client_secret = reddit_secret,
                      username = reddit_user,
                      password= reddit_pass,
                      user_agent = "abghan", check_for_async=False)


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching,
                                                                                    name="世話焼きキツネの仙狐さん"))
    print('We have logged in as {0.user}'.format(bot))


#help command
@bot.slash_command(guild_ids=serverids, name='help', description="get list of avillable commands")
async def helpjson(ctx):
    with open('help.json', 'r') as help_file:
        help_commands = json.load(help_file)
        help_embed = discord.Embed.from_dict(help_commands)
        await ctx.respond(embed=help_embed)


#urban dictionary command
@bot.slash_command(guild_ids=serverids, name='urban', description="Gets a word's definition from Urban Dictionary")
async def urban(ctx, word):
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
@bot.slash_command(guild_ids=serverids, name='reddit', description="Sends a random image from a chosen subreddit")
async def reddit(ctx, subred: Option(str, description="Choose your subreddit", choices=subchoices)):
    subreddit = redditt.subreddit(subred)
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


#ceasercipher encoder
@bot.slash_command(guild_ids=serverids, description="Encodes text using Caesar method")
async def encode(ctx, text: Option(str, "Enter the text you want to encode")):
    ciphertext = CaesarCipher(text, offset=14)
    await ctx.respond(ciphertext.encoded)

  
#ceasercipher decoder
@bot.slash_command(guild_ids=serverids, description="Decodes text using Caesar method")
async def decode(ctx, text: Option(str, "Enter the text you want to decode")):
    ciphertext = CaesarCipher(text, offset=14)
    await ctx.respond(ciphertext.decoded)


#clear masseges
@bot.slash_command(guild_ids=serverids, description="Deletes a specefic amount of messages")
async def clear(ctx, amount: Option(int, "Amount of messages you want to delete", default=1)):
    if ctx.author.guild_permissions.manage_messages:
        await ctx.channel.purge(limit=amount)
        await ctx.respond("Done")
    else:
        await ctx.respond("You don't have enough permissions")


@bot.slash_command(guild_ids=serverids, description="Kicks a member")
@commands.has_permissions(kick_members=True, administrator=True)
async def kick(ctx, member: Option(discord.Member), reason: Option(str, "Reason to kick")):
    if member.id == ctx.author.id:
        await ctx.respond("Bruh why are you kicking yourself :sob:")
    elif member.guild_permissions.administrator:
        await ctx.respond("You cannot kick admins :rofl:")
    else:
        await member.kick(reason=reason)
        await ctx.respond(f"<@{ctx.author.id}> has kicked <@{member.id}> from this server\nReason:{reason}")


      
#unban
@bot.slash_command(guild_ids=serverids, name="unban", description="Unbans a member")
@commands.has_permissions(ban_members=True)
async def unban(ctx,
                id: Option(discord.Member, description="The User ID of the person you want to unban.", required=True)):
    await ctx.defer()
    member = await bot.get_or_fetch_user(id)
    await ctx.guild.unban(member)
    await ctx.respond(f"I have unbanned {member.mention}.")


@unban.error
async def unbanerror(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("get tf outta here "
                          "dont mess")
    else:
        await ctx.respond(f"Something went wrong, I couldn't unban this member or this member isn't banned.")
        raise error



#mute/timeout
@bot.slash_command(guild_ids=serverids, name='timeout', description="mutes / timeouts a member")
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: Option(discord.Member, required=True), reason: Option(str, required=False),
               days: Option(int, max_value=27, default=0, required=False),
               hours: Option(int, default=0, required=False), minutes: Option(int, default=0, required=False),
               seconds: Option(int, default=0,
                               required=False)):  # setting each value with a default value of 0 reduces a lot of the code
    if member.id == ctx.author.id:
        await ctx.respond("You can't timeout yourself masochist!")
        return
    if member.guild_permissions.moderate_members:
        await ctx.respond("Don't mess with admins")
        return
    duration = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    if duration >= timedelta(days=28):  # added to check if time exceeds 28 days
        await ctx.respond("I know he is annoying af but i cant ban him for more than 28 days!",
                          ephemeral=True)  # responds, but only the author can see the response
        return
    if reason == None:
        await member.timeout_for(duration)
        await ctx.respond(
            f"<@{member.id}> has been timed out for {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds by <@{ctx.author.id}>.")
    else:
        await member.timeout_for(duration, reason=reason)
        await ctx.respond(
            f"<@{member.id}> has been timed out for {days} days, {hours} hours, {minutes} minutes, and {seconds} seconds by <@{ctx.author.id}> for '{reason}'.")


@timeout.error
async def timeouterror(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You can't do this! You need to have moderate members permission!")
    else:
        raise error


#unmute
@bot.slash_command(guild_ids=serverids, name='unmute', description="unmutes/untimeouts a member")
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: Option(discord.Member, required=True), reason: Option(str, required=False)):
    if reason == None:
        await member.remove_timeout()
        await ctx.respond(f"<@{member.id}> has been untimed out by <@{ctx.author.id}>.")
    else:
        await member.remove_timeout(reason=reason)
        await ctx.respond(f"<@{member.id}> has been untimed out by <@{ctx.author.id}> for '{reason}'.")


@unmute.error
async def unmuteerror(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You can't do this! You need to have moderate members permissions!")
    else:
        raise error


      
#ban
@bot.slash_command(guild_ids=serverids, name="ban", description="Bans a member")
@commands.has_permissions(ban_members=True, administrator=True)
async def ban(ctx, member: Option(discord.Member, description="Who do you want to ban?"),
              reason: Option(str, description="Why?", required=False)):
    if member.id == ctx.author.id:  # checks to see if they're the same
        await ctx.respond("You can't ban yourself ffs!")
    elif member.guild_permissions.administrator:
        await ctx.respond("u can't ban an admin ! :rolling_eyes:")
    else:
        if reason == None:
            reason = f"None provided by {ctx.author}"
        await member.ban(reason=reason)
        await ctx.respond(
            f"<@{ctx.author.id}>, <@{member.id}> ass has been kicked out successfully from this server!\n\nReason: {reason}")


@ban.error
async def banerror(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("bruh You need to be an admin to use this")
    else:
        await ctx.respond("Something went wrong...")  # most likely due to missing permissions
        raise error


#anime girls api
@bot.slash_command(guild_ids=serverids, description='Sends a random anime girl picture')
async def waifu(ctx, type: Option(str, description="Enter your preferred type", choices=waifuchoices)):
    async with aiohttp.ClientSession() as session:
        request = await session.get(f'https://api.waifu.pics/sfw/{type}')
        testjson = await request.json()
    embed = discord.Embed(title=f"{type}", color=discord.Color.random(), type='image')
    embed.set_image(url=testjson['url'])
    await ctx.respond(embed=embed)

#change bot name
@bot.slash_command(guild_ids=serverids, description="Changes the bot's name")
async def rename(ctx, name):
    await bot.user.edit(username=name)
    await ctx.respond(f"bot usernaem was changed to {name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return


keep_alive()
bot.run(token)
