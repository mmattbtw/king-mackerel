import discord
import discord_slash

import games.exp_data as exp

import games.fishdata as fishdata

from games.fishdata import Bait
from discord import Colour
from discord.ext import commands
from discord_slash import cog_ext, SlashContext, ComponentContext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_button, create_select, create_actionrow, create_select_option, \
    wait_for_component
from core.db_models import User
from etc import discord_formatting as fmt

from etc.custom_embeds import CEmbed

lock = '🔒'
bait_data = fishdata.bait_info
rod_data = fishdata.rod_info


# Users can purchase:
#
# - Fishing Rods
# - Fishing Bait
# - Fishing line? (later update?)

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(description='Opens the shop menu.', guild_ids=[857568078626684928])
    async def shop(self, ctx: SlashContext):
        user, created = User.get_or_create(user_id=ctx.author_id)
        level = exp.get_rounded_level(user.exp)

        if level < 5:
            embed = CEmbed().err(f'Shops unlock at level 5! You are level {level}!')
            await ctx.send(embed=embed)
            return

        embed = CEmbed()
        embed.title = 'Shop Selection'
        embed.description = 'Which shop would you like to visit?'
        embed.colour = Colour.blurple()

        buttons = [
            create_button(style=ButtonStyle.blurple, label='Bait Shop', custom_id='on_shop_bait'),
            create_button(style=ButtonStyle.blurple, label='Rod Shop', custom_id='on_shop_rod')
        ]

        action_row = create_actionrow(*buttons)
        await ctx.send(embed=embed, components=[action_row], hidden=True)

    @cog_ext.cog_component()
    async def on_shop_bait(self, ctx: ComponentContext):
        user, created = User.get_or_create(user_id=ctx.author_id)
        level = exp.get_rounded_level(user.exp)

        # Fishing Bait
        fish_bait_available = []
        fish_bait_locked = []

        for key in bait_data:
            key_data = bait_data.get(key)

            # TODO: Remove for production
            # Only here while we continue to build out this feature.
            #
            # We do not encounter KeyErrors if the dictionaries are
            # properly filled out
            try:
                level_required = key_data['level_required']
                cost = key_data['cost']
                max_rarity = str(key_data['max_rarity'])

                desc = f'Cost: {cost} | Lvl. Req: {level_required} | Max Rarity: {max_rarity}'
            except KeyError:
                continue

            if level_required <= level:
                fish_bait_available.append((key, desc))
            else:
                fish_bait_locked.append((key, level_required, desc))

        bait_selections = []
        for available_option, description in fish_bait_available:
            bait_selections.append(
                create_select_option(str(available_option), value=available_option.value, description=description))
        for locked_option, level, description in fish_bait_locked:
            bait_selections.append(create_select_option(str(locked_option), value=locked_option.value, emoji=lock,
                                                        description=description))

        bait_select = create_select(options=bait_selections, placeholder='Bait Shop', min_values=1, max_values=1,
                                    custom_id='bait_selections')

        embed = discord.Embed()
        embed.title = 'Bait Shop'
        embed.description = 'Select the type of bait you wish to purchase to open ' \
                            'the purchase menu!'
        embed.colour = Colour.green()

        await ctx.edit_origin(embed=embed, components=[create_actionrow(bait_select)], hidden=True)

    @cog_ext.cog_component()
    async def on_shop_rod(self, ctx: ComponentContext):
        await ctx.edit_origin(disabled=True)

        pass

    @cog_ext.cog_component()
    async def bait_selections(self, ctx: ComponentContext):
        button_id = ctx.selected_options[0]

        user, created = User.get_or_create(user_id=ctx.author_id)
        level = exp.get_rounded_level(user.exp)
        coins = user.coins

        # Using selection as an index. A bit of a hacky workaround.
        # Requires that fishdata.bait_info be written in order of the enum values from least to greatest.
        bait = Bait(int(button_id))
        selection_data = bait_data[bait]
        cost = selection_data['cost']
        if coins < cost:
            embed = CEmbed().err('Insufficient balance! You do not have enough coins to purchase any bait.')
            await ctx.edit_origin(embed=embed)
            return

        purchase_buttons = [create_button(style=ButtonStyle.blurple, label='+1', custom_id='bait_1')]
        subtract_buttons = [
            create_button(style=ButtonStyle.secondary, label='-1', custom_id='bait_-1'),
            create_button(style=ButtonStyle.secondary, label='-5', custom_id='bait_-5'),
            create_button(style=ButtonStyle.secondary, label='-10', custom_id='bait_-10'),
            create_button(style=ButtonStyle.secondary, label='-25', custom_id='bait_-25')
        ]

        if coins >= cost * 5:
            purchase_buttons.append(create_button(style=ButtonStyle.blurple, label='+5', custom_id='bait_5'))
        if coins >= cost * 10:
            purchase_buttons.append(create_button(style=ButtonStyle.blurple, label='+10', custom_id='bait_10'))
        if coins >= cost * 25:
            purchase_buttons.append(create_button(style=ButtonStyle.blurple, label='+25', custom_id='bait_25'))

        components = [
            create_actionrow(*purchase_buttons),
            create_actionrow(create_button(style=ButtonStyle.green, label='Checkout', custom_id='checkout'))
        ]

        embed = CEmbed()
        embed.title = 'Bait Shop: ' + str(bait)
        embed.description = f'Click the buttons below to add bait to your shopping cart, then press the green button to checkout!\n\n' \
                            f'{fmt.as_bold_underline("Bait Info:")}\n' \
                            f'- Level Required: {selection_data["level_required"]}\n' \
                            f'- Cost: {selection_data["cost"]}\n' \
                            f'- Max Rarity: {selection_data["max_rarity"]}\n' \
                            f'- Max Rarity Catch Chance: +{selection_data["max_rarity_bonus_multiplier"]:.1%}\n' \
                            f'- Exp Bonus: +{selection_data["exp_bonus_multiplier"]:.1%}\n' \
                            f'- Coin Bonus: +{selection_data["coin_multiplier"]:.1%}\n' \
                            f'- Quality Bonus: +{selection_data["quality_bonus_multiplier"]:.1%}\n'
        embed.set_footer(text=f'Cart: 0x {bait} | Remaining Balance: {coins}')
        embed.colour = Colour.blue()

        await ctx.edit_origin(embed=embed, components=components)

        # Total user cart and update
        count = 0
        while True:
            button_ctx: ComponentContext = await wait_for_component(self.bot, components=components)
            button_id = button_ctx.custom_id

            if button_id == 'checkout':
                # TODO: Send checkout message
                break

            addition_invalid_amt = '\n' + fmt.as_bold('You cannot subtract bait without adding it to your cart first!')
            addition_insufficient_funds = '\n' + fmt.as_bold(
                'Insufficint balance! Please subtract from your cart or checkout!')

            # assumes custom ids of buttons end with the number to increase quantity by.
            amount_increased = int(str(button_id).split('_')[-1])

            # TODO: FIX
            warned = False
            if count + amount_increased < 0:
                if addition_invalid_amt not in embed.description:
                    embed.description = embed.description + addition_invalid_amt
                    embed.colour = Colour.orange()
                    warned = True
                    await button_ctx.edit_origin(embed=embed)
                #button_ctx = await wait_for_component(self.bot, components=components)

            if coins - (cost * amount_increased) < 0:
                if addition_insufficient_funds not in embed.description:
                    embed.description = embed.description + addition_insufficient_funds
                    embed.colour = Colour.red()
                    warned = True
                    await button_ctx.edit_origin(embed=embed)
                #button_ctx = await wait_for_component(self.bot, components=components)

            if not warned:
                count += amount_increased
                coins -= cost * amount_increased

                embed.set_footer(text=f'Cart: {count:,}x {bait} | Remaining Balance: {coins}')
                await button_ctx.edit_origin(embed=embed)

        # Modify embed and award user items

        if count == 0:
            embed = CEmbed()
            embed.colour = Colour.random()
            embed.description = 'See you next time!'
            await button_ctx.edit_origin(embed=embed)
            return

        embed.title = 'Checkout Successful!'
        embed.description = f'Congrats on your purchase of {count:,} {str(bait)}! Now get out there and ' \
                            f'catch some fish!'
        embed.set_footer(text=f'Remaining balance: {coins:,}')
        await button_ctx.edit_origin(embed=embed)


def setup(bot):
    bot.add_cog(Shop(bot))
