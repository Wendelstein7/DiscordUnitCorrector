# Discord Unit Corrector Bot
#
# This bot is licenced under the MIT License [Copyright (c) 2018 Wendelstein7]
#
# This is a Discord bot running python3 using the Discord.py library
# This bot will listen for any messages in Discord that contain non-SI units and when detected, reply with the message converted to SI-Units.
# Are you tired of a car that weighs 100 Stones, is 10 feet high, and can drive 50 miles at 5 degrees freedom?
# Worry no more! Your car weighs 0.64t, is 3.05m high, and can drive 80.47km at -15°C from now on!
# Simply add this bot to your server! You can choose to run it yourself or add the version that is updated and hosted by me [Wendelstein 7]

# The unit conversion library was riginally created by ficolas2, https://github.com/ficolas2, 2018/01/21
# The unit conversion library has been modified and updated by ficolas2 and Wendelstein7, https://github.com/Wendelstein7

# Licenced under: MIT License, Copyright (c) 2018 Wendelstein7 and ficolas2

import datetime
import os
import sys
from datetime import datetime, date

import discord
from discord.ext import commands
from filter import Filter

import unitconversion
import unitpedialib

description = """UnitCorrector: A community-beveloped open source Discord bot that corrects non-SI units to SI ones! Also features a !unitpedia command, allowing users to learn about (all) units."""
bot = commands.Bot(command_prefix='!', description=description)

starttime = datetime.utcnow()
longprefix = ':symbols: UnitCorrector | '
shortprefix = ':symbols: '

credits = '**HydroNitrogen** (GH: `Wendelstein7`, <@378840449152188419>) - _Creator and main current developer_ \n**Shaq** (GH: `Shaquu`, <@197109511239106561>) - _Main current developer_ \n**ficolas** (GH: `ficolas2`, <@192368029366091777>) - _Past developer_ \n ...And other wonderful contributors, see GitHub.'


@bot.event
async def on_ready():
    print('Discord Unit Corrector Bot: Logged in as {} (id: {})\n'.format(
        bot.user.name, bot.user.id))


@bot.event
# Catches send messages and corrects non-SI units if neccesary. Most of the code behind this is in 'unitconversion.py'.
async def on_message(message):
    if bot.user.id is not message.author.id and message.author.bot is False and (message.guild is None or (message.guild is not None and discord.utils.get(message.guild.roles, name='imperial certified') not in message.author.roles)):
        processedMessage = unitconversion.process(message.content)
        if processedMessage is not None:
            correctionText = ("I think " + Filter.apply_strict(message.author.display_name if message.guild is not None else "you") +
                              " meant to say: ```" + Filter.apply_strict(processedMessage) + "```")
            await message.channel.send(correctionText)
    await bot.process_commands(message)


@bot.event
async def on_command(ctx):
    print('[{}] Fired {} by {}'.format(
        datetime.now(), ctx.command, ctx.author))


@bot.command(name='unitcorrector', aliases=['units', 'listunits', 'unitlist'])
# May be converted to a nice embed if needed in the future.
async def unitcorrector(ctx):
    """Lists supported units by the unit corrector bot."""
    supportedUnits = ""
    for unit in unitconversion.units:
        if supportedUnits != "":
            supportedUnits += ", " + unit.getName()
        else:
            supportedUnits += unit.getName()
    await ctx.send(shortprefix + "UnitCorrector automatically detects and corrects users who send non-SI units in their messages.\nThe bot currently supports the following units:\n```" + supportedUnits + "```")


@bot.command(name='uptime', hidden=True)
# May be deprecated, changed or removed as !about already shows the uptime.
async def uptime(ctx):
    """Shows how long this instance of the bot has been online."""
    await ctx.send(shortprefix + 'Uptime\n```Bot started: {}\nBot uptime: {}```'.format(starttime, (datetime.now() - starttime)))


@bot.command(name='contributors', aliases=['credits', 'developers'])
# Will be made a nice embed in the future if there are lots of contributors.
async def contributors(ctx):
    """Lists the  people who have contributed to this bot."""
    embed = discord.Embed(title="UnitCorrector contributors and developers", colour=discord.Colour(
        0xffffff), url="https://github.com/Wendelstein7/DiscordUnitCorrector", description=credits)
    embed.set_thumbnail(url=bot.user.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name='unitpedia')
# Unitpedia! Still needs need a lot of expansion and work. Most of the code behind this is in 'unitpedialib.py'.
async def unitpedia(ctx, *, search: str):
    """Gives information about an unit. Try !unitpedia mi, !unitpedia litre, !unitpedia °C, etc..."""
    result = unitpedialib.lookup(search)
    if result != "notfound":
        await ctx.send(embed=result)
    else:
        await ctx.send(shortprefix + 'Sorry, your search query has not returned any results. Try to search using different words or abbreviations.\n\n*Unitpedia is not complete and needs community submissions. If you want to help expand unitpedia, please visit <https://github.com/Wendelstein7/DiscordUnitCorrector>.*')


@unitpedia.error
async def unitpedia_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(shortprefix + 'You will need to enter a query to search for. Try `!unitpedia metre`, `!unitpedia °F`, `!unitpedia mile²`, etc...')


@bot.command(name='about', aliases=['info'])
# May be changed in the future to be send in DM to prevent malicious use for spam purposes.
async def about(ctx):
    """Shows information about the bot aswell as the relevant version numbers, uptime and useful links."""
    embed = discord.Embed(title="UnitCorrector", colour=discord.Colour(0xffffff), url="https://github.com/Wendelstein7/DiscordUnitCorrector",
                          description="A fully functional public Discord bot that automatically corrects non-SI units (imperial, etc) to SI-ones (metric, etc) This bot will listen for any messages in Discord that contain non-SI units and when detected, reply with the message converted to SI-Units.\n\n*Are you tired of a car that weighs 100 Stones, is 10 feet high, and can drive 50 miles at 5 degrees freedom? Worry no more! Your car weighs 0.64t, is 3.05m high, and can drive 80.47km at -15°C from now on!*")
    embed.set_thumbnail(url=bot.user.avatar_url)
    embed.add_field(name=":information_source: **Commands**",
                    value="Please use the `!help` to list all possible commands!")
    embed.add_field(name=":hash: **Developers**", value=credits)
    embed.add_field(name=":symbols: **Contributing**",
                    value="Want to help with the bot? You're welcome to do so!\n[Visit our GitHub for more information!](https://github.com/Wendelstein7/DiscordUnitCorrector)")
    embed.add_field(name=":new: **Version information**", value="Bot version: `{}`\nDiscord.py version: `{}`\nPython version: `{}`".format(
        date.fromtimestamp(os.path.getmtime('unitbot.py')), discord.__version__, sys.version.split(' ')[0]), inline=True)
    embed.add_field(name=":up: **Uptime information**", value="Bot started: `{}`\nBot uptime: `{}`".format(starttime.strftime(
        "%Y-%m-%d %H:%M:%S"), (datetime.utcnow().replace(microsecond=0) - starttime.replace(microsecond=0))), inline=True)
    embed.add_field(name=":free: **Adding the bot**",
                    value="Want to add this bot to **your** server? [Click here to add it!](https://discordapp.com/oauth2/authorize?client_id=405724335525855232&scope=bot&permissions=67619905)")
    await ctx.send(embed=embed)


# INFO: To run the bot yourself you must enter your bots private token in a (new) file called 'token'
with open('token', 'r') as content_file:
    content = content_file.read()

bot.run(content)
