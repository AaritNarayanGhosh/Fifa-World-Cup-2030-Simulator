import pandas as pd
import numpy as np
import os

class SquadAggregator:
    def __init__(self, players_df, teams_df):
        self.players_df = players_df
        self.teams_df = teams_df
        
    def _assign_players_to_nations(self):
        """
        Since we now have real players mapped to their actual nations,
        we no longer draft. We simply pull the players whose Nationality
        matches the nation.
        """
        # Ensure 'Nation' column matches 'Nationality' from players
        self.players_df = self.players_df.rename(columns={'Nationality': 'Nation'})
        return self.players_df

    def optimize_starting_xi(self, squad_df):
        """
        Greedy positional ranker to select the optimal 11 matching a 4-3-3 formation:
        1 GK, 2 CB, 2 FB, 1 DM, 2 AM/CM, 3 FW
        Remaining players go to bench.
        """
        squad_df = squad_df.copy()
        squad_df['Is_Starter'] = False
        
        formation = {'GK': 1, 'CB': 2, 'FB': 2, 'DM': 1, 'AM': 2, 'FW': 3}
        
        for pos, count in formation.items():
            if pos == 'AM':
                # Allow CMs to act as AMs
                candidates = squad_df[(squad_df['Position'].isin(['AM', 'CM'])) & (~squad_df['Is_Starter'])]
                top_players = candidates.nlargest(count, 'PAV')
            elif pos in ['FW', 'FB']:
                candidates = squad_df[(squad_df['Position'] == pos) & (~squad_df['Is_Starter'])]
                top_players = candidates.nlargest(count, 'PAV')
            else:
                candidates = squad_df[(squad_df['Position'] == pos) & (~squad_df['Is_Starter'])]
                top_players = candidates.nlargest(count, 'PDV')
                
            squad_df.loc[top_players.index, 'Is_Starter'] = True
            
        return squad_df

    def calculate_team_strengths(self, assigned_squads):
        """
        Att_Team = 0.50 * Mean(PAV_FWD) + 0.35 * Mean(PAV_MID) + 0.15 * Mean(PAV_FB)
        Def_Team = 0.25 * PDV_GK + 0.45 * Mean(PDV_CB) + 0.20 * Mean(PDV_DM) + 0.10 * Mean(PDV_FB)
        Bench strength: 10% dampener on base ratings (90% starter + 10% bench).
        """
        team_strengths = []
        nations = assigned_squads['Nation'].unique()
        
        for nation in nations:
            squad = assigned_squads[assigned_squads['Nation'] == nation]
            starters = squad[squad['Is_Starter']]
            bench = squad[~squad['Is_Starter']]
            
            def get_mean(df, metric, positions):
                vals = df[df['Position'].isin(positions)][metric]
                return vals.mean() if not vals.empty else 0.0

            # Starter Ratings
            att_starters = (
                0.50 * get_mean(starters, 'PAV', ['FW']) +
                0.35 * get_mean(starters, 'PAV', ['AM', 'CM', 'DM']) +
                0.15 * get_mean(starters, 'PAV', ['FB'])
            )
            
            def_starters = (
                0.25 * get_mean(starters, 'PDV', ['GK']) +
                0.45 * get_mean(starters, 'PDV', ['CB']) +
                0.20 * get_mean(starters, 'PDV', ['DM', 'CM']) +
                0.10 * get_mean(starters, 'PDV', ['FB'])
            )
            
            # Bench Ratings
            att_bench = (
                0.50 * get_mean(bench, 'PAV', ['FW']) +
                0.35 * get_mean(bench, 'PAV', ['AM', 'CM', 'DM']) +
                0.15 * get_mean(bench, 'PAV', ['FB'])
            )
            
            def_bench = (
                0.25 * get_mean(bench, 'PDV', ['GK']) +
                0.45 * get_mean(bench, 'PDV', ['CB']) +
                0.20 * get_mean(bench, 'PDV', ['DM', 'CM']) +
                0.10 * get_mean(bench, 'PDV', ['FB'])
            )
            
            # 10% Depth Dampener
            att_team = (0.90 * att_starters) + (0.10 * att_bench)
            def_team = (0.90 * def_starters) + (0.10 * def_bench)
            
            team_strengths.append({
                'Nation': nation,
                'Att_Strength': att_team,
                'Def_Strength': def_team
            })
            
        return pd.DataFrame(team_strengths)

    def run_pipeline(self):
        assigned_players = self._assign_players_to_nations()
        
        # Optimize XI for each nation
        optimized_squads = []
        for nation in assigned_players['Nation'].unique():
            squad = assigned_players[assigned_players['Nation'] == nation]
            opt_squad = self.optimize_starting_xi(squad)
            optimized_squads.append(opt_squad)
            
        full_squads = pd.concat(optimized_squads)
        team_matrix = self.calculate_team_strengths(full_squads)
        
        return team_matrix

if __name__ == "__main__":
    players_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'aggregated_player_ratings.csv')
    teams_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'projected_48_teams.csv')
    
    if not os.path.exists(players_path) or not os.path.exists(teams_path):
        print("Error: Missing input files. Run previous sprints.")
    else:
        players_df = pd.read_csv(players_path)
        teams_df = pd.read_csv(teams_path)
        
        aggregator = SquadAggregator(players_df, teams_df)
        team_matrix = aggregator.run_pipeline()
        
        out_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'nation_strength_matrix.csv')
        team_matrix.to_csv(out_path, index=False)
        
        print("==================================================")
        print("Calculated Team Strength Matrix (Top 10 Attacking)")
        print("==================================================")
        print(team_matrix.sort_values('Att_Strength', ascending=False).head(10))
        print(f"\nSaved to {out_path}")
