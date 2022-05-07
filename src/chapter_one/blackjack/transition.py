from inspect import Traceback
import sys

from src.chapter_one.blackjack.constants import Action

from typing import Tuple, Dict, List, Union


# (player sum, used ace as 11, dealer card, stopped)
State = Tuple[str, bool, int, bool]


def f_next_state(x: State, u: str, w: Union[int, str]) -> State:
    """Transitions to the next state

    Note that the transition dynamic is the same for
    every timestep
    """
    s, a, c, h = x

    # if we already stopped playing then
    # nothing changes
    if not h:
        next_state = (s, a, c, h)

    # if the user decides to stop then we transition
    # to a stopped state
    elif u == 'stop':
        next_state = (s, a, c, False)


    # after this point we already know that we
    # are playing h = 1 and the action is 
    # to play u=PLAY

    # if we draw an Ace and our sum can afford
    # using the ace as 11
    elif w == 'A' and int(s) <= 10:
        next_state = (str(int(s)+11), True, c, h)

    # if our current score is over 10 then
    # we need to use the ace as a one
    elif w == 'A' and 10 < int(s) < 21:
        next_state = (str(int(s)+1), a, c, h)

    # if we are hit with an ace and we are on the limit
    # but have used an ace previosuly then we can cast both aces
    # back to 1. Note that this is an artifical case
    # the user will never hit with a 21
    elif w == 'A' and int(s) == 21 and a:
        next_state = (str(int(s)-10+1), False, c, h)

    # if we don't have an ace then we just go bust
    elif w == 'A' and int(s) == 21 and not a:
        next_state = ('BUST', False, c, False)

    # if we currently have an ACE used and the 
    # value with the new delta is under 22
    # we just hapilly take that increase
    elif a and int(s) + w <= 21:
        next_state = (str(int(s)+w), a, c, h)

    # if we have used an ace anf our value now
    # with the addition of the new card exceeds
    # 21 - then we can cast the ACE back to a 1
    # and keep playing
    elif a and int(s) + w > 21:
        next_state = (str(int(s)-10+w), False, c, h)

    # if we dont have an ace and he value of then
    # card can be accommodated then we take the increase
    elif (int(s) + w) <= 21:
        next_state = (str(int(s)+w), a, c, h)

    # if we dont have an ace and the value of the new
    # card exceeds 21 then we go bust
    elif (int(s) + w) > 21:
        if a == True:
            raise ValueError("Investigate. Why do we have a usable ace here? It should had been cast to 1 in previous stages")
        next_state = ('BUST', a, c, False)

    else:
        raise NotImplemented(f"No branching logic for '{x}'")

    return next_state

