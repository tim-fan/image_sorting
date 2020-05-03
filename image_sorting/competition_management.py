'''
class for managing image compeition in app.py
'''

import pandas as pd
import random
import sqlitedict


class CompetitionManager:
    """
    Responsible for match making and recording results.
    Manages an internal db for persistence
    """
    def __init__(self, dbfile='./db.sqlite'):
        self.db = sqlitedict.SqliteDict(dbfile, autocommit=True)

    def __del__(self):
        self.db.close()
        
    def competition_in_progress(self):
        return 'competitors' in self.db.keys()


    def start_competition(self, competitor_names, randomise=True):
        """
        Initialise competitor table from list of names
        """
        if randomise:
            random.shuffle(competitor_names)
        
        competitors = pd.DataFrame(competitor_names, columns=['name'])
        competitors['level'] = 0
        n_competitors = len(competitors.index)
        assert n_competitors > 1, "Error: competition initialised with less than two competitors"

        losers = pd.DataFrame(columns=competitors.columns)

        #setup db tables
        self.db['competitors'] = competitors
        self.db['losers'] = losers
        if 'match_records' not in self.db.keys():
            self.db['match_records'] = pd.DataFrame(columns= ['winner', 'loser', 'timestamp'])

    def get_next_match(self):
        """
        Determine which competitors compete next
        """
        # trial - find the highest level with at least two competitors
        assert self.competition_in_progress(), "Error - no competition running. Call 'start_competition'"
        competitors = self.db['competitors']

        n_competitors_by_level = competitors.level.value_counts()
        next_competition_level = n_competitors_by_level[n_competitors_by_level >= 2].index.max()
        
        next_match_candidates = competitors[competitors.level == next_competition_level]
        if len(next_match_candidates.index) < 2:
            return None #can't make a match
        else: 
            return next_match_candidates.iloc[0:2,].name.values

    def process_result(self, winner, loser):
        """
        Update competitors based on result of a match.
        The winner goes up a level, the loser is removed from 
        competitors table and added to loser table
        Returns updated winners/losers tables
        """
        competitors = self.db['competitors']
        losers = self.db['losers']

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

        self.db['competitors'] = competitors
        self.db['losers'] = losers

        #update record of all results
        match_records = self.db['match_records']
        record = pd.DataFrame([[winner, loser, pd.Timestamp.now()]], columns=['winner', 'loser', 'timestamp'])
        match_records.append(record)
        self.db['match_records'] = match_records

    def get_top_n(self, n):
        """
        Get the current top n images
        """
        competitors = self.db['competitors']
        losers = self.db['losers']
        return pd.concat([
            competitors, losers]
        ).sort_values(
            by='level',
            ascending=False
        ).iloc[0:n].name.values
    
    def get_n_remaining_matches(self):
        return len(self.db['competitors'].index) -1