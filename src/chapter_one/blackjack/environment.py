import networkx as nx
import pandas as pd

from typing import Tuple
from collections import defaultdict
from structlog import get_logger
from functools import reduce

from pandas import DataFrame



logger = get_logger(__name__)


card_dynamics = {
    **{i: 1/13 for i in range(2, 10)},
    10: 4/13,
    'A': 1/13
}

