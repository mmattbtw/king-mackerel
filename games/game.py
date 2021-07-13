import abc

class Game: # Base class for all games
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def payout(self):
        return
