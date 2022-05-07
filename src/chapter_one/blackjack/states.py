import sys
from typing import Tuple, Dict, List

from pandas.core.common import standardize_mapping

from src.chapter_one.blackjack.constants import PLAYER_SUM
from src.chapter_one.blackjack.constants import DEALER_CARD

# (player sum, used ace as 11, dealer card, stopped)
State = Tuple[str, bool, int, bool]


def all_possible_states() -> List[State]:
    """Generates all all possible states

    State = (s, a, c, h)
    """
    for s in PLAYER_SUM:
        for c in DEALER_CARD:

            if (s == 'BUST') or (int(s) < 11):
                a_states = [False]
            else:
                a_states = [True, False]

            if s == 'BUST':
                h_states = [False]
            else:
                h_states = [True, False]

            for a in a_states:
                for h in h_states:
                    state = (s, a, c, h)
                    yield state


def allowed_states(k: int) -> List[State]:
    """Returns a list of allowed states for the timestep k

    Most of the complexity is actually induced by the dual
    nature of the ace A
    """
    # if k = 1 then we have just seen the first card
    # so we are defenitely still playing
    # we basically can have any sum between 2..11 rewith
    # 11 -> have used an ace
    if k == 1:
        states = []
        for c in DEALER_CARD:
            for s in map(str, range(2, 11)):
                states.append((s, False, c, True))
            states.append(('11', True, c, True))

    # for the second timestep it all dependens on what the player
    # did in the first round
    # also note that 21 is just achievable with one A
    elif k == 2:
        states = all_possible_states()
        open_states = [
            (s, a, c, h) for (s, a, c, h) in states
            if (h and s != 'BUST') and not (h and s == '21' and not a) and 
            (h and int(s.replace('BUST', '22')) >= 4) and
            not (h and a and int(s.replace('BUST', '22')) < 11 + k -1)
        ]
        closed_states = []
        for c in DEALER_CARD:
            for s in map(str, range(2, 11)):
                closed_states.append((s, False, c, False))
            closed_states.append(('11', True, c, False))
        states = open_states + closed_states

    elif k in set(range(3, 6 + 1)):
        states = all_possible_states()
        states = [
            (s, a, c, h)
            for (s, a, c, h) in states
            if not (h and int(s.replace('BUST', '22')) < 2 * k)  and
            not (h and a and int(s.replace('BUST', '22')) < 11 + k -1)
        ]

    elif k in set(range(7, 11 + 1)):
        states = all_possible_states()
        states = [
            (s, a, c, h)
            for (s, a, c, h) in states
            if not (h and int(s.replace('BUST', '22')) < 12) and 
            not (h and a and int(s.replace('BUST', '22')) < 11 + k -1)
        ]

    # if k > 11 then we have at least 11 cards which mean 
    # that we can no longer have a usable ace
    else:
        states = all_possible_states()
        states = [
            (s, a, c, h)
            for (s, a, c, h) in states
            if not ((h and int(s.replace('BUST', '22')) < k) or (h and a))
        ]

    return states



def make_terminal_states() -> List[State]:
    """Creates all possible terminal states

    (player sum, used ace as 11, dealer card, stopped)
    State = (s, a, c, h)

    Note:
        h = 0
        s in {2, 3, ..., 11, bust}
        a = _
        c = {2,3,..,A}
    """
    states = [
        (s, a, c, h)
        for s, a, c, h in all_possible_states()
        if not h
    ]
    return states
