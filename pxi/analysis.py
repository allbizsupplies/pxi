
IGNORED_TERMS = [
    "",
    " ",
    "of",
    "x",
    "and",
    "a",
]


HIT_MULTIPLIER = 1
DIRECT_HIT_MULTIPLIER = 2
MISS_MULTIPLIER = 0.5


def calculate_similarity(hits, direct_hits, misses):
    return hits * HIT_MULTIPLIER + direct_hits * DIRECT_HIT_MULTIPLIER - misses * MISS_MULTIPLIER


def compare_terms(a_terms, b_terms):
    """
    Compares two lists of terms by counting the following:

    - misses: the terms found in one list but not the other
    - hits: the terms found in both lists
    - direct_hits: the terms found in the same position in both lists
    """
    length_difference = len(b_terms) - len(a_terms)
    # Make the shorter terms the first terms.
    if length_difference >= 0:
        first_terms = a_terms
        second_terms = b_terms
    else:
        first_terms = b_terms
        second_terms = a_terms
    misses = abs(length_difference)
    direct_hits = 0
    hits = 0
    for i, term in enumerate(first_terms):
        if term == second_terms[i]:
            direct_hits += 1
            hits += 1
        elif term in second_terms:
            hits += 1
        else:
            misses += 1
    return {
        "direct_hits": direct_hits,
        "hits": hits,
        "misses": misses,
    }


def extract_terms(line):
    """
    Split a string into searchable terms.
    """
    terms = []
    components = line.split(" ")
    for component in components:
        normalised_component = component.strip().lower()
        is_ignored_term = normalised_component in IGNORED_TERMS
        is_duplicate_term = normalised_component in terms
        if not (is_ignored_term or is_duplicate_term):
            terms.append(normalised_component)
    return terms
