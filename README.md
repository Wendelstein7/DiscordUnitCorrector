# DiscordUnitCorrector
A fully functional public Discord bot that automatically corrects non-SI units (imperial, etc) to SI-ones (metric, etc)
This bot will listen for any messages in Discord that contain non-SI units and when detected, reply with the message converted to SI-Units.

Are you tired of a car that weighs 100 Stones, is 10 feet high, and can drive 50 miles at 5 degrees freedom?
Worry no more! Your car weighs 0.64t, is 3.05m high, and can drive 80.47km at -15°C from now on!

Simply add this bot to your server! You can choose to run it yourself or use the bot that is updated and hosted by me [Wendelstein 7](https://github.com/Wendelstein7).

## Credits

**The unit conversion library was originally created by ficolas2, https://github.com/ficolas2, 2018/01/21**
**The unit conversion library has been modified and updated by ficolas2 and Wendelstein7, https://github.com/Wendelstein7**

## Cool! Let me add this bot to my server right now!

[You can click here to add the bot hosted by me to your server](https://discordapp.com/oauth2/authorize?client_id=405724335525855232&scope=bot&permissions=67619905)

After you've followed the instructions, the bot will be in your server and there will be a new role 'UnitCorrector'. This role is exclusive to the bot and it should have all the default permissions set the way they are.
You're ready to rock! Write a little story about miles, inches or farenheit and see the bot correcting you!

### Configuration of the bot in your server

To manage and configure what the bot can do, will do and shouldn't do, all you will need to adjust are the permissions.
Don't want the bot to correct in a certain channel? Just disable it's ability to speak!
Want to prevent the bot from correcting a specific person? Give that person a new role named 'imperial certified' and the bot will no longer correct anything spoken by the users that have this role.
That's it!

### Help and information

There are a few nice commands and more are being developed and worked on.
You can see a list of commands by typing !help in the Discord chat or in a direct message to the bot.

Enjoy!

## Collaborate and Help this bots

### Want to help us with developing this bot?

Nice! Feel free to fork this project and make improvements, add features and fix bugs. Once your work is ready, make a PR (Pull Request) to this REPO and we will review and possibly merge it if you did good!
(crappy PRs will be ignored, good PRs will be merged. You will get credits if (parts of) your code got merged.)

### How to run yourself (NOT RECCOMMENDED unless you want to develop)
* Install the main dependency Discord.py using `python3 -m pip install -U discord.py` (make sure you got the rewrite branch!)
* Do `git clone https://github.com/Wendelstein7/KeyStoneBot`.
* Go to the created folder `KeyStoneBot`.
* Create a (text) file named `token`.
* Open it with a text editor and enter your Discord bot token there, and save it.
* Run the bot with `python3 keystonebot.py`.
* boom!

### API reference and documentation:
This bot is running on Python3 using the [Discord.py library](https://github.com/Rapptz/discord.py/tree/rewrite).
IMPORTANT: We are using the `rewrite` branch of Discord.py, keep that in mind!
* https://github.com/Rapptz/discord.py/tree/rewrite
* https://discordpy.readthedocs.io/en/rewrite/api.html
* https://discordpy.readthedocs.io/en/rewrite/ext/commands/api.html
* https://github.com/Rapptz/discord.py/tree/rewrite/examples
* [The Discord.py Discord server](https://discordapp.com/invite/r3sSKJJ)


## Memes

Actually, I developed this bot before I was aware of the metric memes, but now that I've noticed and now that people have brought this to my attention, a few of them belong here, don't they? Send me the best ones so that I can include a !memes command in the future ;)
