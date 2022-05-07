import networkx as nx
import pandas as pd

from typing import Tuple
from collections import defaultdict
from structlog import get_logger
from functools import reduce

from pandas import DataFrame


Node = Tuple[int, bool]


logger = get_logger(__name__)


transition_dynamics = {
    **{i: 1/13 for i in range(2, 10)},
    10: 4/13,
    11: 1/13
}


def _play(g: nx.DiGraph, state: Node) -> nx.DiGraph:
    """
    Recursively plays all of the possible games starting from a certain node

    A particular branch ends whenever we
    are in state that is worth 17 to 21 or goes bust

    In every edge inserted the associated probability transition is also added

    Note: if this function is called then we assume that we are in a state
    that is outside of the range 17...21 and not Bust
    """
    sum_, ace = state

    next_states = defaultdict(lambda: 0)

    for card_value, prob in transition_dynamics.items():

        next_sum = sum_ + card_value

        # if we go over 21, but we have an ace
        # with a score that, by removing the ace,
        # we fall into the range 17-21
        if all([
            next_sum > 21,
            ace or card_value == 11,
            17 <= next_sum - 10 <= 21
        ]):
            next_states[next_sum - 10] += prob

        # if we go over 21, but we have an ace
        # with a score that, by removing the ace,
        # we get a score < 17
        elif all([
            next_sum > 21,
            ace,
            card_value != 11,
            next_sum - 10 < 17
        ]):
            next_states[(next_sum - 10, False)] += prob

        # if we go over 21, but we have an ace
        # with a score that, by removing the ace,
        # we get a score < 17
        elif all([
            next_sum > 21,
            ace,
            card_value == 11,
            next_sum - 10 < 17
        ]):
            next_states[(next_sum - 10, True)] += prob

        elif (next_sum > 21) and not ace:
            next_states['bust'] += prob

        elif 17 <= next_sum <= 21:
            next_states[next_sum] += prob

        else:
            next_states[(next_sum, ace or (card_value == 11))] += prob

    for next_state, prob in next_states.items():
        g.add_edge(state, next_state, p=prob)

        if next_state not in {'bust', 17, 18, 19, 20, 21}:
            g = _play(g, next_state)

    return g


def make_dealer_transition_graph() -> nx.DiGraph:
    """
    initial states :: (int, bool) = (current sum, usable ace)
    """
    logger.info("Creating dealer transition graph")

    g = nx.DiGraph()
    initial_states = [(11, True)] + [(i, False) for i in range(2, 11)]

    logger.info("Initial states")
    for x, y in initial_states:
        logger.info("State", value=x, has_ace=y)

    for state in initial_states:
        g.add_node(state)
        g = _play(g, state)

    logger.info("Graph", nodes=g.number_of_nodes(), edges=g.number_of_edges())

    return g


def calculate_dealer_probabilities(g: nx.DiGraph) -> DataFrame:
    """
    Calculates the dealers probability of going bust or
    obtaining a sum of 17 to 21 as a function of the dealer's
    initial state

    Assumes the dealer follows the following policy:
    * keep asking a card until 17
    """
    initial_states = [(11, True)] + [(i, False) for i in range(2, 11)]
    terminal_states = [17, 18, 19, 20, 21, 'bust']

    data = []

    for source in initial_states:
        for dest in terminal_states:

            prob = 0
            for path in nx.all_simple_paths(g, source, dest):
                path_probabilities = [g.get_edge_data(a, b)['p'] for a, b in zip(path, path[1:])]
                path_probability = reduce(lambda acc, x: acc * x, path_probabilities, 1)
                prob += path_probability

            data.append((source[0], dest, prob))

    df = pd.DataFrame(data, columns=['card', 'score', 'probability'])
    df['score'] = df['score'].astype(str)

    file = '/Users/raufer/rl/rl-training/src/chapter_one/blackjack/resources/dealers_probabilities.pickle'
    df.to_pickle(file)
    logger.info(f"Written '{file}'")

    return df


# g = make_dealer_transition_graph()
# df = calculate_dealer_probabilities(g)
# # print(df)
#
# print(df)
# print(df[df['card'] == 11]['probability'].sum())
