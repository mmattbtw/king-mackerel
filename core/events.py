import datetime
import logging

from discord.ext import commands
from discord_slash import SlashContext

from core.db_models import User

log = logging.getLogger()


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command(self, ctx: SlashContext):
        """Event that creates a user account (if one does not exist) whenever a slash command is used."""
        id = ctx.author_id

        try:
            User.get(User.user_id == id)
        except:
            User.create(user_id=id, coins=0, fish_caught=0, exp=0, created_at=datetime.datetime.utcnow())
            log.debug(f'New user created: {id}')

def setup(bot):
    bot.add_cog(Events(bot))
