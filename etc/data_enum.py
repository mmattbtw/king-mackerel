from enum import Enum

class DataEnum(Enum):
    def __str__(self):
        """Returns a formatted version of the enum name.
        Assumes enum name is capitalized with underscores separating words."""
        if "_" in self.name:
            ret = ''
            for split in self.name.split("_"):
                ret += f'{split.capitalize()} '

            ret = ret.strip()
            return ret

        return self.name.capitalize()

    def __int__(self):
        """Returns the value of this enum."""
        return self.value