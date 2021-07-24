import discord
import logging
import logsetup
import os
import database
import db_models

from games import fishdata
from discord import LoginFailure
from discord.ext.commands import Bot as BotBase
from discord.ext.commands.errors import NoEntryPointError
from discord_slash import SlashCommand
from models.config import Config

cfg = Config()

# Setup logger
logsetup.create_logger()
log = logging.getLogger()

# Test db connection
database.connect()
database.disconnect()

db_models.create_tables()

fishdata.check_prefixes() # Ensure proper formatting of prefixes

class Bot(BotBase):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = False
        intents.presences = False

        super().__init__(
            command_prefix=cfg.prefix,
            owner_ids=cfg.owner_ids,
            intents=intents,
            case_insensitive=True
        )

        self.launch()

    def load_cogs(self):
        self.load_extension('events')
        log.info('Cog loaded: events')

        for cog in os.listdir(os.path.join("../", "cogs/")):
            if cog.endswith(".py"):
                cog_basename = cog.replace('.py', '')
                cog = f"cogs.{cog_basename}"
                try:
                    self.load_extension(cog)
                    log.info("Cog loaded: " + cog_basename)
                except (AttributeError, NoEntryPointError):
                    log.warning(f"{cog} Can not be loaded")

    def launch(self):
        _ = SlashCommand(self, sync_commands=True, sync_on_cog_reload=True)
        self.load_cogs()

        try:
            self.run(cfg.token)
        except LoginFailure:
            log.critical("Invalid bot token.")

bot = Bot() # Calls constructor which launches the bot
