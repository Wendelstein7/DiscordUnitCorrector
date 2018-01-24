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

import discord
from discord.ext import commands
import random

import time
import datetime
from datetime import datetime, date
from datetime import timedelta

import unitconversion

description = """A Discord bot that corrects non-SI units to SI ones!"""
bot = commands.Bot(command_prefix='!', description=description)

starttime = datetime.now()
longprefix = ':symbols: UnitCorrector | '
shortprefix = ':symbols: '

@bot.event
async def on_ready():
    print('Discord Unit Corrector Bot: Logged in as {} (id: {})\n'.format(bot.user.name, bot.user.id))

@bot.event
async def on_message(message):
    if bot.user.id is not message.author.id and discord.utils.get(ctx.guild.roles, name='imperial certified') not in message.author.roles:
        processedMessage = unitconversion.process(message.content)
        if processedMessage is not None:
            correctionText = ("I think " + message.author.name + " meant to say: ```" + processedMessage + "```")
            await message.channel.send(correctionText)
    await bot.process_commands(message)

@bot.command()
async def unitcorrector(ctx):
    """Lists supported units by the unit corrector bot."""
    await ctx.send(shortprefix + 'Unit Corrector\nSupported units are:\n```inch, foot, mile, (all those squared), acre, pint, quart, gallon, foot-pound, pound-force, pound-foot, mph, ounce, pound, stone and degrees freedom```')

@bot.command()
async def uptime(ctx):
    """Shows how long this instance of the bot has been online."""
    runtime = (datetime.now() - starttime)
    await ctx.send(shortprefix + 'Uptime\n```Bot started: {}\nBot uptime: {}```'.format(starttime, runtime))

with open('token', 'r') as content_file: # INFO: To run the bot yourself you must enter your bots private token in a (new) file called 'token'
    content = content_file.read()

bot.run(content)
