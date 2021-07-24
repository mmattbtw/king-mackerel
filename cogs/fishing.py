import discord
import numpy as np

from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from etc import discord_formatting as fmt
from games import fishdata as f
from collections import Counter

from core.db_models import *

log = logging.getLogger()

sims = 100
fish_count = 5000

class Fishing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(description='Play the fishing game! Use /info to learn about the '
                                   'way fishing works.', guild_ids=[857568078626684928])
    async def fish(self, ctx: SlashContext):
        # Get user
        # Determine level
        # Get fishing rod, if any
        user, created = User.get_or_create(user_id=ctx.author_id)
        d = f.FishData(user)

        print(int(d.quality))
        fish = Fish.create(user=user, name=d.name, base_value=d.base_value, catch_value=d.catch_value,
                           rarity=d.rarity.value, weight_kg=d.weight, quality=d.quality, time_caught=d.time_caught,
                           minimum_line_thickness_required=d.line_thickness_required)

        embed = discord.Embed(title='🎣 | Fishing')
        embed.description = d.catch_statement
        embed.colour = d.embed_colour
        await ctx.send(embed=embed)

        # TODO: Add logic for level-ups here. If user has leveled up, send another notification

    @commands.is_owner()
    @cog_ext.cog_slash(description='Simulates the fishing game', guild_ids=[857568078626684928])
    async def sim(self, ctx: SlashContext):
        await ctx.defer()
        sim = sim_avgs_rarities()

        count_rarities = Counter(sim[1])

        await ctx.send(embed=discord.Embed(description=
                                           f'Average net winnings ({sims * fish_count} fish simulated): '
                                           f'{fmt.as_bold(sim[0])}'
                                           f'\nRarities: {count_rarities}'))


def sim_avgs_rarities() -> [float, []]:
    # Runs a simulation, can take ~10 seconds
    values = []
    rarities = []

    for i in range(sims):
        fish_ls = f.get_fish(fish_count)

        for fish in fish_ls:
            values.append(fish.catch_value)
            rarities.append(fish.rarity_data)

        log.debug(f'Fish Simulation Progress: [{i + 1} / {sims}]')

    return [np.average(values), rarities]


def setup(bot):
    bot.add_cog(Fishing(bot))
