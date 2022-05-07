import structlog

from pandas import DataFrame
from typing import Tuple, Dict, List


from src.chapter_one.blackjack.states import all_possible_states, allowed_states
from src.chapter_one.blackjack.transition import f_next_state
from src.chapter_one.blackjack.environment import card_dynamics


# (player sum, used ace as 11, dealer card, stopped)
State = Tuple[str, bool, int, bool]


def p_dealer_sum(df: DataFrame, card: int, sums: List) -> float:
    """
    Calculates the probability of the dealer having
    stopping on any of the given sums starting from card
    """
    sums = list(map(str, sums))
    region = df[
        (df['card'] == card) &
        (df['score'].isin(sums))
    ]
    p = region['probability'].sum()
    return p


def terminal_cost(xn: State, df: DataFrame) -> float:
    """Calculates the terminal cost g_N(x_N)

    Note that:
    * P{dealer′s win} = p(s < dealer′s sum ≤ 21| c )
    * P{player wins}  = 1 - P{dealer′s win}

    In DP we typically solve a minimization problem
    so we construct the problem in a way that forces
    the probability of a player wining as negative
    as possible
    """
    s, a, c, h = xn

    if s == 'BUST':
        cost = 0

    else:
        s = int(s)
        win_scores = [x for x in [17, 18, 19, 20, 21] if x > s]
        p_dealer_win = p_dealer_sum(df, c, win_scores)
        p_player_win = 1 - p_dealer_win
        cost = - p_player_win

    return cost


def expected_timestep_cost(k: int, probs: Dict, J: Dict) -> float:
    """Calculates the expected cost of starting at timestep k

    J_k(x_k) = min_{u_k in U_k(x_k)} E_{with respect to w_k} {gk(xk, uk, wk) + J_{k+1}(fk(xk, uk, wk)}

    Note: the calculation is done for all x_k in Domain(J_k)
    """
    states = allowed_states(k)

    # if we are not playing, there is nothing to choose
    for state in states:
        J = expected_cost(k=k, x=state, J=J)

    return J


def expected_cost(k: int, x: State, J: Dict):
    """Calculates the expecetd cost of being at state s


    We need to first calculate the expected cost
    for every possible actions that we can take in state s

    The expected cost for state x is found by minimizing 
    the 
    """
    (s, a, c, h) = x

    if h:
        actions = ['play', 'stop']
    else:
        actions = ['stop']


    for action in actions:
        J = expected_action_cost(k=k, x=x, u=action, J=J)

    optimal_action, optimal_cost = min([(action, cost) for action, cost in J[k][x].items()], key=lambda x: x[1])

    J[k][x]['.cost'] = optimal_cost
    J[k][x]['.action'] = optimal_action

    return J


def expected_action_cost(k: int, x: State, u: str, J: Dict):
    """Calculates the expecetd cost of taking the action u at state s

    If u='play' then the environment is stochastic and
    we need to run an expectation over the drawn card

    If u='stop' then the environment behaves deterministically
    """
    # deterministic transition
    if u == 'stop':
        J[k][x][u] = J[k+1][f_next_state(x, u, None)]['.cost']

    # stochastic transition - we need to take an expected value
    # with respect the the card draw distribution
    else:
        sum_ = 0
        for w, prob in card_dynamics.items():
            cost = J[k+1][f_next_state(x, u, w)]['.cost']
            sum_ += prob * cost

        J[k][x][u] = sum_

    return J

