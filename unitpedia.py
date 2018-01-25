# The unit information list 'unitpedia' has been created by Wendelstein7, https://github.com/Wendelstein7

# Licenced under: MIT License, Copyright (c) 2018 Wendelstein7 and ficolas2

import re

def lookup(search):
    #TODO Add code that finds the search keyword using the regex in the information articles list. Should return the embedded info.

class InformationArticle:
    def __init__( self, regexsearch, longname, shortname, category, origin, history, definition, isSI, wiki ):
        self.regexSearch = regexsearch
        self.longname = longname
        self.shortname = shortname
        self.category = category
        self.origin = origin
        self.history = history
        self.definition = definition
        self.isSI = isSI
        self.wiki = wiki
        self.embed = discord.Embed(title=longname, colour=discord.Colour(0xc800), url=wiki, description=history)
        self.embed.set_thumbnail(url="botlogo")embed.add_field(name="Defenition", value=definition)
        self.embed.add_field(name="Long Name", value=longname, inline=True)
        self.embed.add_field(name="Abbreviation", value=shortname, inline=True)
        self.embed.add_field(name="Unit category", value=category, inline=True)
        self.embed.add_field(name="Origin", value=origin, inline=True)
        self.embed.add_field(name="SI-Unit", value=isSI, inline=True)

await bot.say(embed=embed)

#This information 'unitpedia' database needs expansion! Please help by putting information from WikiPedia in heref for units not already here!
class InformationArticles:
    articles = []

    #metre
    articles.append(InformationArticle( "(k(ilo)?|c(enti)|?m(illi)?)?m(eters?|etres?)?", "Meter", "m", "distance", "France, 1789", """In the aftermath of the French Revolution (1789), the traditional units of measure used in the Ancien Régime were replaced. The livre monetary unit was replaced by the decimal franc, and a new unit of length was introduced which became known as the metre.""", """Length of the path travelled by light in a vacuum in ​1⁄299792458 of a second.""", True, "https://en.wikipedia.org/wiki/Metre"))

    #foot
    articles.append(InformationArticle( "f(oo|ee)?t|'|′", "Foot", "ft", "distance", "Unknown and/or uncertain.", """Historically the human body has been used to provide the basis for units of length. The foot of a white male is typically about 15.3% of his height, giving a person of 160 cm (5 ft 3 in) a foot of 245 mm and one of 180 cm (5 ft 11 in) a foot of 275 mm.""", """Defined by international agreement as equivalent to 0.3048 meters exactly.""", False, "https://en.wikipedia.org/wiki/Foot_(unit)"))

    #mile
    articles.append(InformationArticle( "mi(les?)?", "Mile", "mi", "distance", "Unknown and/or uncertain.", """The mile was established as part of the 1959 international yard and pound agreement reached by the United States, the United Kingdom, Canada, Australia, New Zealand, and South Africa, which resolved small but measurable differences that had arisen from separate physical standards each country had maintained for the yard.""", """The international mile is precisely equal to 1.609344 km (or 25146/15625 km as a fraction).""", False, "https://en.wikipedia.org/wiki/Mile"))

    #TODO: Add more units...
