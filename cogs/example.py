# import discord
# from discord.ext import commands
# from discord_slash import cog_ext, SlashContext
#
# class Example(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#
#     @cog_ext.cog_slash(name="example", guild_ids=[857568078626684928], description="Hello")
#     async def _help(self, ctx: SlashContext):
#         embed = discord.Embed(title="embed test")
#         await ctx.send(content="test", embeds=[embed])
#
# def setup(bot):
#     bot.add_cog(Help(bot))
