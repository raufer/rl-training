import pandas as pd

from itertools import groupby
from pandas import DataFrame
from structlog import get_logger
from collections import defaultdict

from src.chapter_one.blackjack.cost import terminal_cost, expected_timestep_cost
from src.chapter_one.blackjack.states import make_terminal_states
from src.chapter_one.blackjack.states import allowed_states
from src.chapter_one.blackjack.states import make_terminal_states
from src.chapter_one.blackjack.constants import Action


logger = get_logger(__name__)


def main(dealer_probs: DataFrame):
    """Solves the DP problem for Blackjack

    Assumes the dealer probabilites of wining for each
    initial dealer's card have already been calculated
    and are made available
    """
    N = 22
    J = defaultdict(lambda: defaultdict(lambda: defaultdict()))

    terminal_states = make_terminal_states()
    for state in terminal_states:
        J[N][state]['.cost'] = terminal_cost(state, dealer_probs)
        J[N][state]['.action'] = None

    for k in range(21, 0, -1):
        J = expected_timestep_cost(k=k, probs=probs, J=J)

    _action = lambda x: 'H' if x == 'play' else 'S'
    
    # construct the solution
    data_ace = []
    data_no_ace = []
    for k, d in J.items():
        if k == 2:
            for x, dd in d.items():
                s, a, c, h = x
                if h and a:
                    data_ace.append((f'A-{s}', c, _action(dd['.action'])))
                elif h and not a:
                    data_no_ace.append((s, c, _action(dd['.action'])))

    data = data_no_ace + data_ace


    data = sorted(data, key=lambda x: int(x[0]) if 'A' not in x[0] else 10*int(x[0].replace('A-', '')))

    rows = []
    for k, gx in groupby(data, key=lambda x: x[0]):
        rows.append({'index': k, **{x[1]: x[2] for x in gx}})

    df = pd.DataFrame(rows)
    df = df.set_index('index')

    file = '/Users/raufer/rl/rl-training/src/chapter_one/blackjack/resources/solution.pickle'
    df.to_pickle(file)
    logger.info(f"Written '{file}'")




if __name__ == '__main__':

    file = '/Users/raufer/rl/rl-training/src/chapter_one/blackjack/resources/dealers_probabilities.pickle'
    probs = pd.read_pickle(file)

    main(
        dealer_probs=probs
    )
