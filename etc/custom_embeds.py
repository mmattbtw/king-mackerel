from discord import Embed, Colour

class CEmbed(Embed):
    def err(self, description=None):
        self.colour = Colour.red()
        if description is not None:
            self.description = description

        return self