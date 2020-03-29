#!/usr/bin/env python
import random

def _is_odd(integer):
    return integer % 2 == 1

def _run_single_match(competitor_a, competitor_b, compare):
    """
    One competitor challenges another. Return the winner
    """
    if competitor_b is None:
        return competitor_a
    else:
        return compare(competitor_a, competitor_b)

def _run_single_round(competitors, compare):
    """
    Runs a single round.
    Competitors are matched randomly into one-on-one challenges, and the winners are returned from this function
    For odd numbers of competitors, the last one is taken as a winner by default
    Inputs: the competitor elements and a comparison function
    """
    
    #pad with 'None' for odd-lengthed lists
    # (last element will win competition against 'None' by default)
    if _is_odd(len(competitors)):
        competitors += [None]
    
    #convert list of competitors to pairwise matches
    matches = zip(competitors[::2], competitors[1::2])
    
    winners = [_run_single_match(a,b, compare) for a,b in matches]
    
    return winners

def run_tournament(competitors, best_n=1, compare=max):
    """
    Run a single elimination tournament between the given list of competitors and the given comparison function
    Will complete when number of remaining competitors is less than 'best_n'
    """
    while len(competitors) > best_n:
        random.shuffle(competitors)
        competitors = _run_single_round(competitors, compare)
    return competitors
