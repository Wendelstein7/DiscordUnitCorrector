# The unit information list 'unitpedia' has been created by Wendelstein7, https://github.com/Wendelstein7

# Licenced under: MIT License, Copyright (c) 2018 Wendelstein7 and ficolas2

import discord
import re

def lookup(search):
    for art in InformationArticles.articles:
        if art.regexSearch.fullmatch(search):
            return art.embed
        
    return "notfound"
    #TODO: Add code that finds the search keyword using the regex in the information articles list. Should return the 'embed' of the found InformationArticle.

class InformationArticle:
    def __init__( self, regexsearch, longname, shortname, category, origin, history, definition, isSI, wiki ):
        self.regexSearch = re.compile(regexsearch)
        self.longname = longname
        self.shortname = shortname
        self.category = category
        self.origin = origin
        self.history = history
        self.definition = definition
        self.isSI = isSI
        self.wiki = wiki
        self.embed = discord.Embed(title=longname, colour=discord.Colour(0xc800), url=wiki, description=('{}\n\n[For more information, refer WikiPedia.]({})'.format(history, wiki)))
        self.embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/405724335525855232/c8c782f4c2de5d221d4beb203829ed9c.webp?size=256")
        self.embed.add_field(name="Defenition", value=definition)
        self.embed.add_field(name="Long Name", value=longname, inline=True)
        self.embed.add_field(name="Abbreviation", value=shortname, inline=True)
        self.embed.add_field(name="Unit category", value=category, inline=True)
        self.embed.add_field(name="Origin", value=origin, inline=True)
        self.embed.add_field(name="SI-Unit", value=isSI, inline=True)

# This information 'unitpedia' database needs expansion! Please help by putting information from WikiPedia in here for units not already here!
class InformationArticles:
    articles = []

    #metre
    articles.append(InformationArticle( "(k(ilo)?|c(enti)?|m(illi)?)?m(eters?|etres?)?", "Meter", "m", "Distance", "France, 1789", """In the aftermath of the French Revolution (1789), the traditional units of measure used in the Ancien Régime were replaced. The livre monetary unit was replaced by the decimal franc, and a new unit of length was introduced which became known as the metre.""", """Length of the path travelled by light in a vacuum in ​1⁄299792458 of a second.""", "Yes", "https://en.wikipedia.org/wiki/Metre"))

    #foot
    articles.append(InformationArticle( "f(oo|ee)?t|'|′", "Foot", "ft", "Distance", "Unknown and/or uncertain.", """Historically the human body has been used to provide the basis for units of length. The foot of a white male is typically about 15.3% of his height, giving a person of 160 cm (5 ft 3 in) a foot of 245 mm and one of 180 cm (5 ft 11 in) a foot of 275 mm.""", """Defined by international agreement as equivalent to 0.3048 meters exactly.""", "No", "https://en.wikipedia.org/wiki/Foot_(unit)"))

    #mile
    articles.append(InformationArticle( "mi(les?)?", "Mile", "mi", "Distance", "Unknown and/or uncertain.", """The mile was established as part of the 1959 international yard and pound agreement reached by the United States, the United Kingdom, Canada, Australia, New Zealand, and South Africa, which resolved small but measurable differences that had arisen from separate physical standards each country had maintained for the yard.""", """The international mile is precisely equal to 1.609344 km (or 25146/15625 km as a fraction).""", "No", "https://en.wikipedia.org/wiki/Mile"))

    #litre
    articles.append(InformationArticle( "(k(ilo)?|c(enti)?|m(illi)?)?L((iter|itre|tr)s?)?", "Litre", "L", "Volume", "France, 1795", "The litre was introduced in France in 1795 as one of the new \"republican units of measurement\" and defined as one cubic decimetre. One litre of liquid water has a mass of almost exactly one kilogram, due to the gram being defined in 1795 as one cubic centimetre of water at the temperature of melting ice.", "A litre is defined as a special name for a cubic decimetre or 10 centimetres × 10 centimetres × 10 centimetres, (1 L ≡ 1 dm³ ≡ 1000 cm³).", "Derived from an SI unit", "https://en.wikipedia.org/wiki/Litre"))

    #degrees celcius
    articles.append(InformationArticle( "(°|º|degrees?)? ?(celcius|centigrade|c|science)", "Celcius Scale", "°C", "Temperature", "Sweden and France, 1742 - 1744", "In 1742, Swedish astronomer Anders Celsius (1701–1744) created a temperature scale which was the reverse of the scale now known by the name \"Celsius\": 0 represented the boiling point of water, while 100 represented the freezing point of water. In 1743, the Lyonnais physicist Jean-Pierre Christin was working independently of Celsius, and developed a scale where zero represented the freezing point of water and 100 represented the boiling point of water. In 1744, coincident with the death of Anders Celsius, the Swedish botanist Carl Linnaeus (1707–1778) reversed Celsius's scale.", "The Celsius scale was based on 0 °C for the freezing point of water and 100 °C for the boiling point of water at 1 atm pressure.", "Derived from an SI unit", "https://en.wikipedia.org/wiki/Celsius"))
    
    #degrees fahrenheit
    articles.append(InformationArticle( "((°|º|deg(ree)?s?) ?)?(fahrenheit|freedom|f)", "Fahrenheit scale", "°F", "Temperature", "Germany, 1724", "Fahrenheit proposed his temperature scale in 1724, basing it on two reference points of temperature. In his initial scale (which is not the final Fahrenheit scale), the zero point was determined by placing the thermometer in a mixture \"of ice, of water, and of ammonium chloride (salis Armoniaci) or even of sea salt\". This combination forms a eutectic system which stabilizes its temperature automatically: 0 °F was defined to be that stable temperature. The second point, 96 degrees, was approximately the human body's temperature (sanguine hominis sani, the blood of a healthy man).", "On the Fahrenheit scale, the freezing point of water is 32 degrees Fahrenheit (°F) and the boiling point is 212 °F (at standard atmospheric pressure). A degree on the Fahrenheit scale is 1⁄180 of the interval between the freezing point and the boiling point.", "No", "https://en.wikipedia.org/wiki/Fahrenheit"))
    
    #degrees kelvin
    articles.append(InformationArticle( "((°|º|deg(ree)?s?) ?)?(kelvin|k)", "Kelvin scale", "K", "Temperature", "Great Britain, 1848", "In 1848, William Thomson, who later was made Lord Kelvin, wrote in his paper, On an Absolute Thermometric Scale, of the need for a scale whereby \"infinite cold\" (absolute zero) was the scale's null point, and which used the degree Celsius for its unit increment. Kelvin calculated that absolute zero was equivalent to −273 °C on the air thermometers of the time. This absolute scale is known today as the Kelvin thermodynamic temperature scale.", "Until 2018, the kelvin was defined as the fraction 1/273.16 of the thermodynamic temperature of the triple point of water (0.01 °C or 32.018 °F). In other words, it was defined such that the triple point of water is exactly 273.16 K. On 16 November 2018, a new definition was adopted, in terms of a fixed value of the Boltzmann constant. For legal metrology purposes, the new definition will officially come into force on 20 May 2019.", "Yes", "https://en.wikipedia.org/wiki/Kelvin")
    
                    

    # TODO: Add more units...
    # example:
    # articles.append(InformationArticle( "regex", "Long name", "abbreviation", "type of unit", "origin (country, year)", "History of the unit.", "The way this unit is defined", "Is this an SI unit? 'Yes', 'No' or 'Derived from SI'", "Link to the wikipedia page."))
