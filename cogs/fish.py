import discord
import numpy as np
import logging

from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from etc import discord_formatting as fmt
from games import fishdata as f
from collections import Counter

log = logging.getLogger()

sims = 100
fish_count = 5000

class Fish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Name is just /fish -- does NOT show in /command list
    @cog_ext.cog_slash(description='Play the fishing game! Use /info to learn about the '
                                   'way fishing works.', guild_ids=[857568078626684928])
    async def fish(self, ctx: SlashContext):
        fish = f.Fish()

        embed = discord.Embed(title='🎣 | Fishing')
        embed.description = f"""{fish.catch_statement}\n\n{str(fish)}"""
        embed.colour = fish.embed_colour
        await ctx.send(embed=embed)

    # Name is /fish sim -- does show in /command list
    @commands.is_owner()
    @cog_ext.cog_slash(description='Simulates the fishing game', guild_ids=[857568078626684928])
    async def sim(self, ctx: SlashContext):
        await ctx.defer()
        sim = sim_avgs_rarities()

        count_rarities = Counter(sim[1])

        await ctx.send(embed=discord.Embed(description=
                                           f'Average net winnings ({sims * fish_count} fish simulated): '
                                           f'{fmt.as_bold(sim[0]):.2f}'
                                           f'\nRarities: {count_rarities}'))

def sim_avgs_rarities() -> [float, []]:
    # Runs a simulation, can take ~10 seconds
    values = []
    rarities = []

    for i in range(sims):
        fish_ls = f.get_fish(fish_count)

        for fish in fish_ls:
            values.append(fish.value)
            rarities.append(fish.rarity)

        log.debug(f'Fish Simulation Progress: [{i + 1} / {sims}]')

    return [np.average(values), rarities]

def setup(bot):
    bot.add_cog(Fish(bot))
