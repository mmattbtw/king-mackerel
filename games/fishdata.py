import math
from dataclasses import dataclass

import numpy as np
import random

from etc import discord_formatting as fmt
from etc.data_enum import DataEnum
from discord.colour import Colour

from core.db_models import *

log = logging.getLogger()

class RarityType(DataEnum):
    TRASH = 0
    VERY_COMMON = 1
    COMMON = 2
    UNCOMMON = 3
    RARE = 4
    VERY_RARE = 5
    ULTRA_RARE = 6
    EPIC = 7
    MYTHICAL = 8
    LEGENDARY = 9

class QualityData(DataEnum):
    UNSELLABLE = 0
    BAD = 1
    POOR = 2
    AVERAGE = 3
    GOOD = 4
    EXCELLENT = 5

    def __int__(self):
        return self.value

    def __str__(self):
        return str(self.name).capitalize()

    def multiplier(self):
        switcher = {
            self.UNSELLABLE: 0.0,
            self.BAD: 0.5,
            self.POOR: 0.7,
            self.AVERAGE: 0.95,
            self.GOOD: 1.0,
            self.EXCELLENT: 1.2
        }

        return switcher.get(self)

all_rarities = [x for x in RarityType]

@dataclass
class Bait:
    id: str
    level_required: int
    cost: int
    max_rarity: int
    luck: float
    exp_multiplier: float
    coin_multiplier: float

    def __str__(self):
        return self.formatted_name()

    def formatted_name(self):
        splits = self.id.split(' ')
        ret = ''
        for s in splits:
            ret += s.capitalize() + ' '

        return ret.strip()

    def max_rarity_enum(self):
        return RarityType(self.max_rarity)

    def get_probability_set(self) -> [(RarityType, float)]:
        unweighted = []
        for i in range(self.max_rarity + 1):
            result = -3 * math.sqrt(i) + 10
            if i >= self.max_rarity - 2:
                result += self.luck / ((self.max_rarity + 1) - i)

            unweighted.append(result)

        # Normalize values
        probs = np.array(unweighted)
        probs /= np.sum(probs)

        map = []
        for i in range(self.max_rarity + 1):
            map.append((RarityType(i), probs[i]))

        return map

bait_info = [
    Bait(id='small worm', level_required=5, cost=10, max_rarity=int(RarityType.COMMON), luck=0.0, exp_multiplier=0.0, coin_multiplier=0.0),
    Bait(id='large worm', level_required=7, cost=25, max_rarity=int(RarityType.UNCOMMON), luck=0.0, exp_multiplier=0.0, coin_multiplier=0.0),
    Bait(id='small shrimp', level_required=11, cost=35, max_rarity=int(RarityType.RARE), luck=0.05, exp_multiplier=0.0, coin_multiplier=0.0),
    Bait(id='large shrimp', level_required=16, cost=45, max_rarity=int(RarityType.RARE), luck=0.1, exp_multiplier=0.0, coin_multiplier=0.03),
    Bait(id='giant shrimp', level_required=22, cost=50, max_rarity=int(RarityType.VERY_RARE), luck=0.13, exp_multiplier=0.0, coin_multiplier=0.05),
    Bait(id='frozen finger mullet', level_required=30, cost=65, max_rarity=int(RarityType.VERY_RARE), luck=0.15, exp_multiplier=0.1, coin_multiplier=0.07),
    Bait(id='live finger mullet', level_required=41, cost=75, max_rarity=int(RarityType.ULTRA_RARE), luck=0.21, exp_multiplier=0.16, coin_multiplier=0.11),
    Bait(id='leech', level_required=48, cost=90, max_rarity=int(RarityType.ULTRA_RARE), luck=0.28, exp_multiplier=0.2, coin_multiplier=0.18),
    Bait(id='frozen mackerel', level_required=56, cost=115, max_rarity=int(RarityType.ULTRA_RARE), luck=0.35, exp_multiplier=0.24, coin_multiplier=0.24),
    Bait(id='live mackerel', level_required=65, cost=150, max_rarity=int(RarityType.EPIC), luck=0.50, exp_multiplier=0.40, coin_multiplier=0.35),
    Bait(id='single hook lure', level_required=71, cost=200, max_rarity=int(RarityType.EPIC), luck=0.75, exp_multiplier=0.52, coin_multiplier=0.41),
    Bait(id='double hook lure', level_required=80, cost=275, max_rarity=int(RarityType.EPIC), luck=0.90, exp_multiplier=0.65, coin_multiplier=0.50),
    Bait(id='reflective lure', level_required=87, cost=375, max_rarity=int(RarityType.MYTHICAL), luck=1.00, exp_multiplier=0.80, coin_multiplier=0.74),
    Bait(id='scented lure', level_required=93, cost=500, max_rarity=int(RarityType.MYTHICAL), luck=1.27, exp_multiplier=1.00, coin_multiplier=0.95),
    Bait(id='blood stained lure', level_required=100, cost=750, max_rarity=int(RarityType.MYTHICAL), luck=1.50, exp_multiplier=1.25, coin_multiplier=1.17),
    Bait(id='naked ballyhoo', level_required=110, cost=1000, max_rarity=int(RarityType.LEGENDARY), luck=2.00, exp_multiplier=1.75, coin_multiplier=1.62)
]

# Ensure name lengths are no more than 25 characters and that other discord API limitations are accounted for.
def validate_bait():
    if len(bait_info) > 25:
        raise Exception('Cannot have >25 fish bait options')

    bad_names = []
    for bait in bait_info:
        if len(bait.id) > 25:
            bad_names.append(bait.id)

    if len(bad_names) > 0:
        raise Exception('(Bait validation error) - names present that are >25 characters: ' + str(bad_names))

validate_bait()

def get_bait_by_id(name):
    return next(filter(lambda bait: bait.id == name, bait_info), None)

# TODO: FishingRod data
class FishingRod(DataEnum):
    pass

rod_info = {

}

def select_random_quality():
    options = [QualityData.UNSELLABLE, QualityData.BAD, QualityData.POOR, QualityData.AVERAGE, QualityData.GOOD, QualityData.EXCELLENT]
    weights = [0.05, 0.05, 0.1, 0.15, 0.45, 0.2]

    rng = np.random.default_rng()
    res = rng.choice(options, p=weights, replace=True)
    return res.value

names_trash = ['glass bottle', 'rock', 'seaweed', 't-shirt', 'piece of plastic', 'worn rag', 'bloody rag',
               'shoe', 'used hairbrush', 'shard of glass', 'plastic bottle', 'barnacle encrusted watch', 'sponge',
               'horeshoe', 'pair of worn panties', 'plastic bag', 'styrofoam cup', 'piece of coral']
names_vc = ['pinfish', 'black bass', 'spot', 'sardine', 'blue crab', 'carp', 'sand shark', 'striped bass',
            'crawfish', 'snapper', 'grouper', 'goldfish', 'clown fish', 'angelfish', 'piranha', 'blue tang']
names_c = ['salmon', 'bluefish', 'pigfish', 'mackerel', 'clam', 'cod', 'halibut', 'herring', 'scallop',
           'marlin', 'yellow heartfish']
names_uc = ['barracuda', 'pipefish', 'catfish', 'salmon', 'swordfish', 'buffalo fish', 'butterfish', 'oyster',
            'sea trout', 'albacore tuna', 'skate']
names_r = ['lobster', 'bluefin tuna', 'goat fish', 'pufferfish', 'hawk fish', 'anemone fish', 'stingray',
           'siamese fighter fish', 'clown tigerfish', 'zebra angelfish', 'neon fish']
names_vr = ['yellowfin tuna', 'long-nosed hawk fish', 'double bar goat fish', 'hammerhead shark']
names_ur = ['rockfish', 'sea turtle', 'dolphin', 'long-nosed butterfly fish', 'porcupine fish']
names_e = ['lionfish', 'rainbow trout', 'giant sea bass', 'long lost ancient artifact']
names_m = ['betta fish', 'european sea sturgeon', 'smalltooth sawfish', 'red handfish', 'ornate sleeper ray']
names_l = ['king mackerel', 'deep sea dragonfish']

# Extensions
for x in names_uc:
    names_vr.append(f'giant {x}')  # giant barracuda, giant catfish, etc.

for x in names_r, names_vr:
    names_e.append(f'giant {x}')

for x in names_ur:
    names_m.append(f'giant {x}')

# Replace _'s with fish name

pfx_trash = ['Aw man, you caught a _', 'Rats, another _',
             'Unlucky, looks like another _', 'How much litter is in the sea? Another _',
             'A _? I could\'ve sworn it was a big catch this time.', 'Unfortuante, yet another _']
pfx_vc = ['Ah, another catch and release. You caught a _', 'These waters have so many _ around.',
          'Meh, looks like another _']
pfx_c = ['Oh neat, looks like you caught a _', 'Oh, another _.']
pfx_uc = ['Cool! You caught a _', 'Not half bad, a _', 'Nice catch mate. A _!']
pfx_r = ['Very nice, you caught a _', 'Neato! A _!']
pfx_vr = ['Wow! You caught a _! Nice!', 'Wow, you don\'t see these often. It\'s a _!',
          'Hot diggity dawg, you caught a _!']
pfx_ur = ['No way! You caught a _!!', 'I haven\'t seen one of these in a while! A _!',
          'Amazing! A _! Nice catch!']
pfx_e = ['Superb!! A _!!', 'Congrats! This _\'s worth a lot!',
         'I haven\'t seen a _ in ages! Nice catch mate!']
pfx_m = ['SUPER! It\'s a wild _!!', 'INCREDIBLE!! A _ at this time of day?? Wow!!',
         'FANTASTIC!! You managed to catch a _!!']
pfx_l = ['WOW!!! You caught a _!!!', 'EXCELLENT!! What a site to behold!!! It\'s a _!!',
         'UNBELIEVABLE!! A wild _! In these waters!!!']

pfx_list = [pfx_trash, pfx_vc, pfx_c, pfx_uc, pfx_r, pfx_vr, pfx_ur, pfx_e, pfx_m, pfx_l]

pstfx_trash = ['Better luck next time', 'At least ya tried', 'Maybe you don\'t eat tonight...',
               'Throw that in the bin']
pstfx_vc = ['Not too shabby', 'It\'s edible I guess', 'Better than nothing', 'Just throw \'em back',
            'You can do better.']
pstfx_c = ['Not bad, but these waters have more to offer.']
pstfx_uc = ['You\'re gonna have a feast with that one!']
pstfx_r = ['Congrats on the nice catch!']
pstfx_vr = ['Super nice catch mate!']
pstfx_ur = ['Incredible catch mate!']
pstfx_e = ['Fantastic catch!', 'Quick, let\'s get a picture! Say cheeeeese!']
pstfx_m = ['Amazing! Now you just need to catch a legendary!']
pstfx_l = ['We need to get in the paper!', 'Monumental!!', 'I can\'t believe this is happening!']

color_trash = Colour.dark_grey()
color_vc = Colour.from_rgb(167, 255, 166)  # Very light green
color_c = Colour.from_rgb(73, 222, 71)  # Normal green
color_uc = Colour.from_rgb(45, 224, 117)  # Mint green
color_r = Colour.from_rgb(52, 231, 247)  # Sky blue
color_vr = Colour.from_rgb(52, 133, 247)  # Moderately deep blue, not too deep
color_ur = Colour.from_rgb(88, 29, 207)  # Rich, royal purple
color_e = Colour.from_rgb(255, 252, 71)  # Bright yellow
color_m = Colour.from_rgb(255, 33, 114)  # Red with a hint of pink
color_l = Colour.from_rgb(255, 92, 33)  # Strong orange

# Description of values:
#
# Names: All possible item/fish names
# Prefixes: Statements/exclamations that form the first part of the sentence. "You caught a ....!"
# Postfixes: Random chance of being applied to the end of the prefix. Statements that add extra flavor to the game.
# Color: Color of the embed sent out to the user
# Probability: A weighted probability of selection. All probabilities do NOT need to add up to 1.00 as they are normalized.
# Base Value: The value of the item/fish before any bonus multipliers are weighed in from rods, events, etc.
# Base Exp Value: Value of exp received, before any bonuses.
# Weights: 2 weights, in kilograms, of the items/fish that can be caught. Values are inclusive ranges and will be selected at random.

data = {
    RarityType.TRASH: {
        "names": names_trash,
        "prefixes": pfx_trash,
        "postfixes": pstfx_trash,
        "color": color_trash,
        "probability": 0.20,
        "base_value": 0,
        "base_exp_value": 0,
        "line_thickness_mm": 0.00,
        "weights": [0.1, 2.0]
    },
    RarityType.VERY_COMMON: {
        "names": names_vc,
        "prefixes": pfx_vc,
        "postfixes": pstfx_vc,
        "color": color_vc,
        "probability": 0.15,
        "base_value": 5,
        "base_exp_value": 1,
        "line_thickness_mm": 0.00,
        "weights": [0.1, 2.0]
    },
    RarityType.COMMON: {
        "names": names_c,
        "prefixes": pfx_c,
        "postfixes": pstfx_c,
        "color": color_c,
        "probability": 0.12,
        "base_value": 10,
        "base_exp_value": 3,
        "line_thickness_mm": 0.10,
        "weights": [1.0, 3.5]
    },
    RarityType.UNCOMMON: {
        "names": names_uc,
        "prefixes": pfx_uc,
        "postfixes": pstfx_uc,
        "color": color_uc,
        "probability": 0.10,
        "base_value": 30,
        "base_exp_value": 9,
        "line_thickness_mm": 0.30,
        "weights": [2.5, 7.0]
    },
    RarityType.RARE: {
        "names": names_r,
        "prefixes": pfx_r,
        "postfixes": pstfx_r,
        "color": color_r,
        "probability": 0.07,
        "base_value": 65,
        "base_exp_value": 15,
        "line_thickness_mm": 0.40,
        "weights": [5.5, 15.0]
    },
    RarityType.VERY_RARE: {
        "names": names_vr,
        "prefixes": pfx_vr,
        "postfixes": pstfx_vr,
        "color": color_vr,
        "probability": 0.05,
        "base_value": 110,
        "base_exp_value": 30,
        "line_thickness_mm": 0.50,
        "weights": [10.0, 22.0]
    },
    RarityType.ULTRA_RARE: {
        "names": names_ur,
        "prefixes": pfx_ur,
        "postfixes": pstfx_ur,
        "color": color_ur,
        "probability": 0.03,
        "base_value": 250,
        "base_exp_value": 65,
        "line_thickness_mm": 0.70,
        "weights": [20.0, 35.0]
    },
    RarityType.EPIC: {
        "names": names_e,
        "prefixes": pfx_e,
        "postfixes": pstfx_e,
        "color": color_e,
        "probability": 0.015,
        "base_value": 400,
        "base_exp_value": 110,
        "line_thickness_mm": 1.00,
        "weights": [30.0, 55.0]
    },
    RarityType.MYTHICAL: {
        "names": names_m,
        "prefixes": pfx_m,
        "postfixes": pstfx_m,
        "color": color_m,
        "probability": 0.005,
        "base_value": 1200,
        "base_exp_value": 325,
        "line_thickness_mm": 1.40,
        "weights": [50.0, 110.0]
    },
    RarityType.LEGENDARY: {
        "names": names_l,
        "prefixes": pfx_l,
        "postfixes": pstfx_l,
        "color": color_l,
        "probability": 0.0001,
        "base_value": 15000,
        "base_exp_value": 1750,
        "line_thickness_mm": 2.50,
        "weights": [100.0, 500.0]
    }
}

def check_prefixes():
    for p in pfx_list:
        for s in p:
            if "_" not in s:
                log.warning(f"Formatting Error for {p}: _ not present in: {s}")

keys = [x for x in data.keys()]

class FishData:
    def __init__(self, fishing_rod: FishingRod, bait: FishingBaitInventory):
        # The order in which these properties lay are very specific as self.rarity needs to be assigned
        # before self.__select_index() can be used, etc.
        self.rarity = self.get_random_rarity()
        self.data = data[self.rarity]

        self.base_value = self.data['base_value']
        self.catch_value = self.__select_value()
        self.name = self.__select_name()
        self.embed_colour = self.data['color']
        self.time_caught = datetime.datetime.utcnow()
        self.quality = select_random_quality()
        self.weight = self.__select_weight()
        self.line_thickness_required = self.data['line_thickness_mm']

        self.catch_statement = self.__get_catch_statement()

    def __select_name(self):
        """Returns a random name for this fish based on the fish's rarity"""
        choices = self.data['names']
        return random.choice(choices)

    def __select_value(self):
        """Returns the value of the fish"""
        base_value = self.data['base_value']
        # TODO: Get user fishing rods and apply any relevant bonuses.
        return base_value

    def __select_exp_value(self):
        base_exp_value = self.data['base_exp_value']
        # TODO: Get user fishing rods, events, etc. and apply any relevant bonuses.
        return base_exp_value

    def __get_catch_statement(self):
        """Returns a statement for how the fish was caught. This is output directly to the user."""
        name = self.name
        # Capitalize name if legendary
        if self.rarity == RarityType.LEGENDARY:
            name = name.upper()

        # Get a random statement and replace the _ in each with an emboldened version of the fish name.
        prefix = random.choice(self.data['prefixes'])
        bld_fish_name = fmt.as_bold(name)

        prefix = prefix.replace('_', bld_fish_name).strip()

        # Don't add duplicate punctuation
        if not prefix.endswith(tuple(['!', '.', '?'])):
            prefix += '.'

        # Grammar - Formatting is finnicky here
        if name.startswith(('a', 'e', 'i', 'o', 'u')):
            if f'a {fmt.as_bold(name.lower())}' in prefix.lower():
                statement = prefix.replace(f'a {fmt.as_bold(name)}', f'an {fmt.as_bold(name)}')

        self.name = name  # TODO: May not be needed?
        statement = prefix

        # Postfix
        chance_postfix = 0.3
        if random.random() <= chance_postfix:
            postfix = random.choice(self.data['postfixes'])

            # Don't add duplicate punctuation
            if not postfix.endswith(tuple(['!', '.', '?'])):
                postfix += '.'

            statement += f' {postfix}'

        return statement

    def __select_weight(self):
        weights = self.data['weights']

        # Select random between range and round to 1 decimal place.
        selection = np.random.uniform(weights[0], weights[1])
        return round(selection, 1)

    @staticmethod
    def get_random_rarity():
        rng = np.random.default_rng()

        selection = rng.choice(keys, 1, p=get_probabilities(), replace=True).astype(RarityType)
        return selection[0]

    @staticmethod
    def get_random_rarities(n):
        """Gets a list of rarities. n is the count"""
        ret = []
        for i in range(n):
            ret.append(FishData.get_random_rarity())

        return ret


def get_probabilities():
    probs = []
    for rarity_data in data.values():
        probs.append(rarity_data['probability'])

    # Normalize values to 1
    probs = np.array(probs)
    probs /= probs.sum()

    return probs


def expected_net_winnings(cost, n) -> float:
    """Calculates average expected payout via simulation"""
    sim = get_fish(n)

    net_wins = []
    for fish in sim:
        net_wins.append(fish.catch_value - cost)

    return np.average(net_wins)


def get_fish(n):
    """Returns a list of n random fish. Randomness is weighted based on rarity"""
    ls = []
    for i in range(n):
        f = FishData(None)
        ls.append(f)

    return ls
