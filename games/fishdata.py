import numpy as np
import random
import logging
import time

from etc import discord_formatting as fmt
from enum import Enum
from discord.colour import Colour

log = logging.getLogger()

class Rarity(Enum):
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

    def __int__(self):
        return self.value

    def __str__(self):
        if "_" in self.name:
            ret = ''
            for split in self.name.split("_"):
                ret += f'{split.capitalize()} '

            ret = ret.strip()
            return ret

        return self.name.capitalize()

#       (rarity, probability, value)
data = [(Rarity.TRASH, 0.20, 0),
        (Rarity.VERY_COMMON, 0.15, 5),
        (Rarity.COMMON, 0.12, 10),
        (Rarity.UNCOMMON, 0.10, 30),
        (Rarity.RARE, 0.07, 65),
        (Rarity.VERY_RARE, 0.05, 110),
        (Rarity.ULTRA_RARE, 0.03, 250),
        (Rarity.EPIC, 0.015, 400),
        (Rarity.MYTHICAL, 0.005, 1200),
        (Rarity.LEGENDARY, 0.0001, 15000)]  # 50x more rare than mythical

names_trash = ['glass bottle', 'rock', 'seaweed', 't-shirt', 'piece of plastic', 'worn rag', 'bloody rag',
               'shoe', 'used hairbrush', 'shard of glass', 'plastic bottle', 'barnacle encrusted watch', 'sponge',
               'horeshoe', 'pair of worn panties', 'plastic bag', 'styrofoam cup', 'piece of coral']
names_vc = ['pinfish', 'black bass', 'spot', 'sardine', 'blue crab', 'carp', 'sand shark', 'striped bass',
            'crawfish', 'snapper', 'grouper', 'goldfish', 'clown fish', 'angelfish', 'piranha', 'blue tang']
names_common = ['salmon', 'bluefish', 'pigfish', 'mackerel', 'clam', 'cod', 'halibut', 'herring', 'scallop',
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
    names_vr.append(f'giant {x}') # giant barracuda, giant catfish, etc.

for x in names_r, names_vr:
    names_e.append(f'giant {x}')

for x in names_ur:
    names_m.append(f'giant {x}')

# "You caught a..."
names = {
    Rarity.TRASH: names_trash,
    Rarity.VERY_COMMON: names_vc,
    Rarity.COMMON: names_common,
    Rarity.UNCOMMON: names_uc,
    Rarity.RARE: names_r,
    Rarity.VERY_RARE: names_vr,
    Rarity.ULTRA_RARE: names_ur,
    Rarity.EPIC: names_e,
    Rarity.MYTHICAL: names_m,
    Rarity.LEGENDARY: names_l
}

# Replace _'s with fish name
prefixes = {
    Rarity.TRASH: ['Aw man, you caught a _', 'Rats, another _',
                   'Unlucky, looks like another _', 'How much litter is in the sea? Another _',
                   'A _? I could\'ve sworn it was a big catch this time.', 'Unfortuante, yet another _'],
    Rarity.VERY_COMMON: ['Ah, another catch and release. You caught a _', 'These waters have so many _ around.',
                         'Meh, looks like another _'],
    Rarity.COMMON: ['Oh neat, looks like you caught a _', 'Oh, another _.'],
    Rarity.UNCOMMON: ['Cool! You caught a _', 'Not half bad, a _', 'Nice catch mate. A _!'],
    Rarity.RARE: ['Very nice, you caught a _', 'Neato! A _!'],
    Rarity.VERY_RARE: ['Wow! You caught a _! Nice!', 'Wow, you don\'t see these often. It\'s a _!',
                       'Hot diggity dawg, you caught a _!'],
    Rarity.ULTRA_RARE: ['No way! You caught a _!!', 'I haven\'t seen one of these in a while! A _!',
                        'Amazing! A _! Nice catch!'],
    Rarity.EPIC: ['Superb!! A _!!', 'Congrats! This _\'s worth a lot!',
                  'I haven\'t seen a _ in ages! Nice catch mate!'],
    Rarity.MYTHICAL: ['SUPER! It\'s a wild _!!', 'INCREDIBLE!! A _ at this time of day?? Wow!!',
                      'FANTASTIC!! You managed to catch a _!!'],
    Rarity.LEGENDARY: ['WOW!!! You caught a _!!!', 'EXCELLENT!! What a site to behold!!! It\'s a _!!',
                       'UNBELIEVABLE!! A wild _! In these waters!!!']
}

def check_prefixes():
    for p in prefixes.values():
        for s in p:
            if "_" not in s:
                log.warning(f"Formatting Error for {p}: _ not present in: {s}")

postfixes = {
    Rarity.TRASH: ['Better luck next time', 'At least ya tried', 'Maybe you don\'t eat tonight...',
                   'Throw that in the bin'],
    Rarity.VERY_COMMON: ['Not too shabby', 'It\'s edible I guess', 'Better than nothing', 'Just throw \'em back',
                         'You can do better.'],
    Rarity.COMMON: ['Not bad, but these waters have more to offer.'],
    Rarity.UNCOMMON: ['You\'re gonna have a feast with that one!'],
    Rarity.RARE: ['Congrats on the nice catch!'],
    Rarity.VERY_RARE: ['Super nice catch mate!'],
    Rarity.ULTRA_RARE: ['Incredible catch mate!'],
    Rarity.EPIC: ['Fantastic catch!', 'Quick, let\'s get a picture! Say cheeeeese!'],
    Rarity.MYTHICAL: ['Amazing! Now you just need to catch a legendary!'],
    Rarity.LEGENDARY: ['We need to get in the paper!', 'Monumental!!', 'I can\'t believe this is happening!']
}

embed_colors = {
    Rarity.TRASH: Colour.dark_grey(),
    Rarity.VERY_COMMON: Colour.from_rgb(167, 255, 166), # Very light green
    Rarity.COMMON: Colour.from_rgb(73, 222, 71), # Normal green
    Rarity.UNCOMMON: Colour.from_rgb(45, 224, 117), # Mint green
    Rarity.RARE: Colour.from_rgb(52, 231, 247), # Sky blue
    Rarity.VERY_RARE: Colour.from_rgb(52, 133, 247), # Moderately deep blue, not too deep
    Rarity.ULTRA_RARE: Colour.from_rgb(88, 29, 207), # Rich, royal purple
    Rarity.MYTHICAL: Colour.from_rgb(255, 33, 114), # Red with a hint of pink
    Rarity.LEGENDARY: Colour.from_rgb(255, 92, 33) # Strong orange
}

class Fish:
    def __init__(self):
        # The order in which these properties lay are very specific as self.rarity needs to be assigned
        # before self.__select_index() can be used, etc.
        self.rarity = self.get_random_rarity()
        # The constant index which accesses certain collections inside this file, based on rarity.
        self.__data_idx = self.__select_index()

        self.value = self.__select_value()
        self.name = self.__select_name()
        self.embed_colour = self.__get_embed_colour()
        self.time_caught = time.gmtime()

        self.__probability = self.__select_probability()
        self.__catch_prefix = self.__get_catch_statement()
        self.__catch_postfix = self.__get_catch_postfix()
        self.catch_statement = f'{self.__catch_prefix} {self.__catch_postfix}'

    def __str__(self):

        """Prints out a table of data for this fish, excluding the name"""
        ret = fmt.as_bold('Value:') + f' {format(self.value, ",")}\n' + \
                                      fmt.as_bold('Rarity:') + f' {str(self.rarity)}'

        return ret

    def __select_name(self):
        """Returns a random name for this fish based on the fish's rarity"""
        choices = names.get(self.rarity)
        return random.choice(choices)

    def __select_value(self):
        """Returns the value of the fish"""
        return data[self.__data_idx][2]

    # TODO: This specific value is actually not normalized. May not even be needed in code.
    def __select_probability(self):
        """Returns the weighted probability of selecting this fish, normalized such that
        all probabilities add up to 1 and are independent of each other."""
        return data[self.__data_idx][1]

    def __select_index(self):
        """Returns the index at which the data for the corresponding rarity lies.
        All indicies of all collections in this class are in order from least to most rare,
        so this index will remain the same for all collections.

        This keeps us from having to use multiple long-winded switches or other means of
        accessing information that is not O(1)."""
        return int(self.rarity)

    def __select_data(self):
        return data[self.__select_index()]

    def __get_catch_statement(self):
        """Returns a statement for how the fish was caught"""
        name = self.name
        # Capitalize name if legendary
        if self.rarity == Rarity.LEGENDARY:
            name = name.upper()

        # Get a random statement and replace the _ in each with an emboldened version of the fish name.
        statement = random.choice(prefixes.get(self.rarity)).replace('_', fmt.as_bold(name)).strip()

        # Don't add duplicate punctuation
        if not statement.endswith(tuple(['!', '.', '?'])):
            statement += '.'

        # Grammar - Formatting is finnicky here
        if name.startswith(('a', 'e', 'i', 'o', 'u')):
            if f'a {fmt.as_bold(name.lower())}' in statement.lower():
                statement = statement.replace(f'a {fmt.as_bold(name)}', f'an {fmt.as_bold(name)}')

        self.name = name
        return statement

    __chance_postfix = 0.3

    def __get_catch_postfix(self):
        if random.random() <= self.__chance_postfix:
            postfix = random.choice(postfixes.get(self.rarity))

            # Don't add duplicate punctuation
            if not postfix.endswith(tuple(['!', '.', '?'])):
                postfix += '.'

            return postfix

        return ''

    def __get_embed_colour(self):
        return embed_colors.get(self.rarity)

    @staticmethod
    def get_random_rarity():
        rng = np.random.default_rng()

        selection = rng.choice(keys, 1, p=probs, replace=True).astype(Rarity)
        return selection[0]

    @staticmethod
    def get_random_rarities(n):
        """Gets a list of rarities. n is the count"""
        ret = []
        for i in range(n):
            ret.append(Fish.get_random_rarity())

        return ret


keys = [x for x, y, z in data]
probs = [y for x, y, z in data]

# Normalize values to 1
probs = np.array(probs)
probs /= probs.sum()

def expected_net_winnings(cost, n) -> float:
    """Calculates average expected payout via simulation"""
    sim = get_fish(n)

    net_wins = []
    for fish in sim:
        net_wins.append(fish.value - cost)

    return np.average(net_wins)


def get_fish(n):
    """Returns a list of n random fish. Randomness is weighted based on rarity"""
    ls = []
    for i in range(n):
        f = Fish()
        ls.append(f)

    return ls
