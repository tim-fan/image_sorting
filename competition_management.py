'''
Functions for managing image compeition in app.py
'''

import pandas as pd
import random

def start_competition(competitor_names):
    """
    Initialise competitor table from list of names
    """
    random.shuffle(competitor_names)
    competitors = pd.DataFrame(competitor_names, columns=['name'])
    competitors['level'] = 0
    n_competitors = len(competitors.index)
    assert n_competitors > 1, "Error: competition initialised with less than two competitors"

    losers = pd.DataFrame(columns=competitors.columns)
    return competitors, losers

def get_next_match(competitors):
    """
    Determine which competitors compete next
    """
    # trial - find the highest level with at least two competitors
    n_competitors_by_level = competitors.level.value_counts()
    next_competition_level = n_competitors_by_level[n_competitors_by_level >= 2].index.max()
    
    next_match_candidates = competitors[competitors.level == next_competition_level]
    if len(next_match_candidates.index) < 2:
        return None #can't make a match
    else: 
        return next_match_candidates.iloc[0:2,].name

def process_result(winner, loser, competitors, losers):
    """
    Update competitors based on result of a match.
    The winner goes up a level, the loser is removed from 
    competitors table and added to loser table
    Returns updated winners/losers tables
    """
    assert winner in competitors.name.values, "Given winner is not in list of competitors"
    assert loser in competitors.name.values, "Given loser is not in list of competitors"
    
    #winner levels up
    competitors.loc[competitors.name == winner,'level'] += 1
    
    #loser is removed from competitor table and added to losers table
    losers = losers.append(competitors.loc[competitors.name == loser,])
    competitors = competitors.drop(
        competitors.index[competitors.name==loser],
        inplace=False
    )
    return competitors, losers