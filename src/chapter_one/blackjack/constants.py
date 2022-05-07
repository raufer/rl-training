from enum import Enum


DEALER_CARD = list(range(2, 12))

PLAYER_SUM = list(map(str, range(2, 22))) + ['BUST']


class Action(Enum):
    PLAY = 'PLAY'
    STOP = 'STOP'

