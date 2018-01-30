import discord
import re

END_NUMBER_REGEX = re.compile("-?[0-9]+([\,\.][0-9]+)?\s*$")

class InformationArticle:
    def __init__( self, dict ):
        self.name = dict["Name"]
        self.symbol = dict["Symbol"]
        self.category = dict["Category"]
        self.origin = dict["Origin"]
        self.history = dict["History"]
        self.definition = dict["Definition"]
        self.isSI = dict["SI"]
        self.wiki = dict["Wiki"]
        self.embed = discord.Embed(title=self.name, colour=discord.Colour(0xc800), url=self.wiki, description=self.history)
        self.embed.set_thumbnail(url="botlogo")
        self.embed.add_field(name="Definition", value=self.definition)
        self.embed.add_field(name="Long Name", value=self.name, inline=True)
        self.embed.add_field(name="Abbreviation", value=self.symbol, inline=True)
        self.embed.add_field(name="Unit category", value=self.category, inline=True)
        self.embed.add_field(name="Origin", value=self.origin, inline=True)
        self.embed.add_field(name="SI-Unit", value=self.isSI, inline=True)

class Unit:
    def __init__( self, dict, unitTypes ):
        self._unitType = unitTypes[ dict["Type"] ]
        self._toSIMultiplication = dict["SI mul"]
        if "SI add" in dict:
            self._toSIAddition = dict["SI add"]
        else:
            self._toSIAddition = 0
        self.targeted = dict["Targeted"]
        self._regex = re.compile( "(" + dict["Regex"] + ")(?![a-z]|[0-9])", re.IGNORECASE )
        self.information = InformationArticle( dict );

    def toMetric( self, value ):
        SIValue = ( value + self._toSIAddition ) * self._toSIMultiplication
        if self._toSIAddition == 0 and SIValue == 0:
            return
        return self._unitType.getString( SIValue )
        
    def find( self, text ):
        match = self._regex.match( text )
        return match is not None

    def convert( self, message ):
        originalText = message.getText()
        iterator = self._regex.finditer( originalText )
        replacements = []
        for find in iterator:
            numberResult = END_NUMBER_REGEX.search( originalText[ 0 : find.start() ] )
            if numberResult is not None:
                metricValue = self.toMetric( float( numberResult.group().replace(",", ".") ) )
                if metricValue is None:
                    continue
                repl = {}
                repl[ "start" ] = numberResult.start()
                repl[ "text"  ] = metricValue
                repl[ "end" ] = find.end()
                replacements.append(repl)
        if len(replacements)>0:
            lastPoint = 0
            finalMessage = ""
            for repl in replacements:
                finalMessage += originalText[ lastPoint: repl[ "start" ] ] + repl[ "text" ]
                lastPoint = repl["end"]
            finalMessage += originalText[ lastPoint : ]
            message.setText(finalMessage)
            
    def getEmbed( self ):
        return self.information.embed
