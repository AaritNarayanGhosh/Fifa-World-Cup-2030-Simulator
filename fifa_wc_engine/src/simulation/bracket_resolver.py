import pandas as pd
import numpy as np

class BracketResolver:
    def __init__(self):
        pass
        
    def pair_round_of_32(self, advancing_teams_df):
        """
        Takes the 32 advancing teams and pairs them up.
        For simulation speed, we rank them 1 to 32 based on group stage performance 
        (Pts, GD, GF) and pair 1 vs 32, 2 vs 31, etc. 
        This avoids the massive FIFA lookup table for 3rd place teams while 
        still rewarding group stage performance.
        """
        sorted_teams = advancing_teams_df.sort_values(
            by=['Rank', 'Pts', 'GD', 'GF'], 
            ascending=[True, False, False, False]
        )
        
        team_list = sorted_teams['Nation'].tolist()
        matchups = []
        
        # Pair 1 vs 32, 2 vs 31, ... 16 vs 17
        for i in range(16):
            matchups.append((team_list[i], team_list[31 - i]))
            
        return matchups

    def progress_bracket(self, round_matchups, match_results_dict):
        """
        Given the matchups and the results (who won), pair the next round.
        match_results_dict: { (TeamA, TeamB): Winner }
        """
        winners = []
        for match in round_matchups:
            tA, tB = match
            # lookup who won
            # The key could be (tA, tB) or (tB, tA) depending on how it was saved
            if (tA, tB) in match_results_dict:
                winners.append(match_results_dict[(tA, tB)])
            elif (tB, tA) in match_results_dict:
                winners.append(match_results_dict[(tB, tA)])
            else:
                raise ValueError(f"Result for {tA} vs {tB} not found.")
                
        # Next round pairings: Winner of Match 1 vs Winner of Match 2, etc.
        next_round = []
        for i in range(0, len(winners), 2):
            next_round.append((winners[i], winners[i+1]))
            
        return next_round
