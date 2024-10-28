""" Functions for testing different methods and approaches used for string-based detection of code similarity """

import difflib
from jellyfish import (levenshtein_distance, damerau_levenshtein_distance, hamming_distance, jaro_similarity, jaro_winkler_similarity)


