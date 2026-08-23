import pandas as pd
import numpy as np

class GroupStageResolver:
    def __init__(self):
        pass

    def compute_standings(self, match_results):
        """
        match_results: list of dicts with 
        ['Group', 'Team_A', 'Team_B', 'Goals_A', 'Goals_B']
        """
        records = {}
        for m in match_results:
            group = m['Group']
            tA = m['Team_A']
            tB = m['Team_B']
            gA = m['Goals_A']
            gB = m['Goals_B']

            if tA not in records: records[tA] = {'Group': group, 'Pts': 0, 'GD': 0, 'GF': 0}
            if tB not in records: records[tB] = {'Group': group, 'Pts': 0, 'GD': 0, 'GF': 0}

            records[tA]['GF'] += gA
            records[tB]['GF'] += gB
            records[tA]['GD'] += (gA - gB)
            records[tB]['GD'] += (gB - gA)

            if gA > gB:
                records[tA]['Pts'] += 3
            elif gA == gB:
                records[tA]['Pts'] += 1
                records[tB]['Pts'] += 1
            else:
                records[tB]['Pts'] += 3

        df = pd.DataFrame.from_dict(records, orient='index').reset_index()
        df.rename(columns={'index': 'Nation'}, inplace=True)

        # Sort by Pts, GD, GF. 
        # (Head-to-head is skipped for speed in this Monte Carlo, GD usually suffices)
        df = df.sort_values(by=['Group', 'Pts', 'GD', 'GF'], ascending=[True, False, False, False])
        
        # Rank within group
        df['Rank'] = df.groupby('Group').cumcount() + 1
        return df

    def get_advancing_teams(self, standings_df):
        """
        Top 2 from each group (24 teams) + 8 best 3rd placed teams.
        Total = 32 teams.
        """
        top_2 = standings_df[standings_df['Rank'] <= 2].copy()
        
        thirds = standings_df[standings_df['Rank'] == 3].copy()
        thirds = thirds.sort_values(by=['Pts', 'GD', 'GF'], ascending=[False, False, False])
        best_8_thirds = thirds.head(8)
        
        advancing = pd.concat([top_2, best_8_thirds])
        
        # We also need a fast way to know which group the thirds came from
        # for bracket placement. 
        return advancing, best_8_thirds['Group'].tolist()
