import numpy as np
import pandas as pd
import time
import os

class VectorizedMonteCarloEngine:
    def __init__(self, num_simulations=25000):
        self.N = num_simulations
        self.base_goals = 1.35
        
    def load_data(self, teams_path, draw_path):
        self.teams_df = pd.read_csv(teams_path)
        self.draw_df = pd.read_csv(draw_path)
        
        # Merge to get strengths aligned with groups
        self.tourney_df = self.draw_df.merge(self.teams_df, on='Nation')
        
        # Assign a numeric ID to each team (0 to 47)
        self.tourney_df['Team_ID'] = np.arange(48)
        
        self.att = self.tourney_df['Att_Strength'].values
        self.dfn = self.tourney_df['Def_Strength'].values
        
        self.att_mean = self.att.mean()
        self.def_mean = self.dfn.mean()
        
        self.team_names = self.tourney_df['Nation'].values
        self.groups = self.tourney_df['Group'].values
        
    def setup_group_stage_fixtures(self):
        """
        Pre-computes the 72 group stage matchups.
        12 groups, 4 teams each (0,1,2,3).
        Matchups per group: (0,1), (0,2), (0,3), (1,2), (1,3), (2,3)
        """
        matchups_a = []
        matchups_b = []
        
        for g in range(12):
            offset = g * 4
            for i in range(3):
                for j in range(i+1, 4):
                    matchups_a.append(offset + i)
                    matchups_b.append(offset + j)
                    
        self.gs_a = np.array(matchups_a)
        self.gs_b = np.array(matchups_b)
        
        # Precompute lambdas for these 72 matches
        # shape: (72,)
        self.gs_lambda_a = self.base_goals * (self.att[self.gs_a] / self.att_mean) * (self.def_mean / self.dfn[self.gs_b])
        self.gs_lambda_b = self.base_goals * (self.att[self.gs_b] / self.att_mean) * (self.def_mean / self.dfn[self.gs_a])
        
        # Broadcast to shape (72, N)
        self.gs_lambda_a = np.tile(self.gs_lambda_a[:, None], (1, self.N))
        self.gs_lambda_b = np.tile(self.gs_lambda_b[:, None], (1, self.N))

    def run_group_stage(self):
        # 1. Simulate all 72 matches across N tournaments simultaneously
        # goals shape: (72, N)
        goals_a = np.random.poisson(self.gs_lambda_a)
        goals_b = np.random.poisson(self.gs_lambda_b)
        
        # 2. Points mapping
        pts_a = np.where(goals_a > goals_b, 3, np.where(goals_a == goals_b, 1, 0))
        pts_b = np.where(goals_b > goals_a, 3, np.where(goals_a == goals_b, 1, 0))
        
        # 3. Aggregate stats: shape (48, N)
        team_pts = np.zeros((48, self.N), dtype=np.int32)
        team_gd = np.zeros((48, self.N), dtype=np.int32)
        team_gf = np.zeros((48, self.N), dtype=np.int32)
        
        np.add.at(team_pts, self.gs_a, pts_a)
        np.add.at(team_pts, self.gs_b, pts_b)
        
        gd_a = goals_a - goals_b
        gd_b = goals_b - goals_a
        np.add.at(team_gd, self.gs_a, gd_a)
        np.add.at(team_gd, self.gs_b, gd_b)
        
        np.add.at(team_gf, self.gs_a, goals_a)
        np.add.at(team_gf, self.gs_b, goals_b)
        
        return team_pts, team_gd, team_gf

    def _get_lambdas(self, teams_a, teams_b):
        """Vectorized lambda lookup for knockout matches."""
        l_a = self.base_goals * (self.att[teams_a] / self.att_mean) * (self.def_mean / self.dfn[teams_b])
        l_b = self.base_goals * (self.att[teams_b] / self.att_mean) * (self.def_mean / self.dfn[teams_a])
        return l_a, l_b

    def simulate_knockout_round(self, match_a, match_b):
        """
        match_a, match_b are arrays of shape (N,) containing team IDs for each tournament.
        Returns the winner array of shape (N,).
        """
        l_a, l_b = self._get_lambdas(match_a, match_b)
        
        g_a = np.random.poisson(l_a)
        g_b = np.random.poisson(l_b)
        
        # Tie-breaker (Extra Time + Penalties combined proxy)
        # If g_a == g_b, 50/50 flip (biased by quality in a full model, 50/50 here for extreme speed)
        ties = (g_a == g_b)
        tie_breakers = np.random.rand(self.N) > 0.5
        
        a_wins = (g_a > g_b) | (ties & tie_breakers)
        
        winners = np.where(a_wins, match_a, match_b)
        return winners

    def run_tournaments(self):
        start_time = time.time()
        self.setup_group_stage_fixtures()
        
        team_pts, team_gd, team_gf = self.run_group_stage()
        
        # To resolve group standings and 3rd place teams, we use a scoring metric to rank them globally.
        # Max pts is 9. Group score = Pts * 10000 + GD * 100 + GF
        # Adding a group-winner bonus so we can extract top 32 trivially.
        # But wait, we need top 2 from each group + top 8 thirds.
        # We can rank within groups first.
        
        metric = team_pts * 10000 + team_gd * 100 + team_gf
        # Shape: (48, N)
        
        # Reshape to (12 groups, 4 teams, N)
        metric_grouped = metric.reshape(12, 4, self.N)
        
        # Argsort within groups (descending). Output shape: (12, 4, N)
        # Using -metric_grouped for descending
        ranks = np.argsort(-metric_grouped, axis=1)
        
        # We need the actual Team IDs. 
        # Base IDs for each group
        base_ids = np.arange(12).reshape(12, 1, 1) * 4
        ranked_team_ids = base_ids + ranks
        
        # Top 2 teams from each group
        # Shape: (12, 2, N)
        top2_ids = ranked_team_ids[:, 0:2, :]
        top2_flat = top2_ids.reshape(24, self.N) # 24 teams
        
        # 3rd place teams
        # Shape: (12, N)
        thirds_ids = ranked_team_ids[:, 2, :]
        thirds_metric = np.take_along_axis(metric_grouped, ranks[:, 2:3, :], axis=1).reshape(12, self.N)
        
        # Sort the 12 thirds to get top 8
        thirds_ranks = np.argsort(-thirds_metric, axis=0) # shape (12, N)
        top8_thirds_idx = thirds_ranks[0:8, :] # shape (8, N)
        
        # Gather the actual team IDs for the top 8 thirds
        top8_thirds_ids = np.take_along_axis(thirds_ids, top8_thirds_idx, axis=0) # shape (8, N)
        
        # Combine to get the 32 advancing teams
        advancing_32 = np.vstack((top2_flat, top8_thirds_ids)) # shape (32, N)
        
        # We can pair them up: 1st vs 32nd, 2nd vs 31st, etc.
        # Since advancing_32 is ordered (Group A 1st, Group A 2nd ... then thirds), 
        # pairing opposite ends works well as a pseudo-seeding.
        
        r32_teams = advancing_32
        
        # Track stages reached
        # Shape: (48, N). Boolean arrays
        reached_r32 = np.zeros((48, self.N), dtype=bool)
        for i in range(32):
            reached_r32[r32_teams[i, :], np.arange(self.N)] = True
            
        # ROUND OF 32
        r16_teams = np.zeros((16, self.N), dtype=np.int32)
        for i in range(16):
            r16_teams[i] = self.simulate_knockout_round(r32_teams[i], r32_teams[31-i])
            
        # ROUND OF 16
        qf_teams = np.zeros((8, self.N), dtype=np.int32)
        for i in range(8):
            qf_teams[i] = self.simulate_knockout_round(r16_teams[i], r16_teams[15-i])
            
        # QUARTERFINALS
        sf_teams = np.zeros((4, self.N), dtype=np.int32)
        for i in range(4):
            sf_teams[i] = self.simulate_knockout_round(qf_teams[i], qf_teams[7-i])
            
        # SEMIFINALS
        final_teams = np.zeros((2, self.N), dtype=np.int32)
        for i in range(2):
            final_teams[i] = self.simulate_knockout_round(sf_teams[i], sf_teams[3-i])
            
        # FINAL
        champions = self.simulate_knockout_round(final_teams[0], final_teams[1])
        
        time_taken = time.time() - start_time
        print(f"Ran {self.N} simulations in {time_taken:.2f} seconds.")
        
        # Aggregate results
        champs_count = np.bincount(champions, minlength=48)
        finals_count = np.zeros(48)
        sf_count = np.zeros(48)
        qf_count = np.zeros(48)
        r16_count = np.zeros(48)
        
        for i in range(2): np.add.at(finals_count, final_teams[i], 1)
        for i in range(4): np.add.at(sf_count, sf_teams[i], 1)
        for i in range(8): np.add.at(qf_count, qf_teams[i], 1)
        for i in range(16): np.add.at(r16_count, r16_teams[i], 1)
        
        r32_count = reached_r32.sum(axis=1)
        
        results = pd.DataFrame({
            'Nation': self.team_names,
            'Win_%': (champs_count / self.N) * 100,
            'Final_%': (finals_count / self.N) * 100,
            'SF_%': (sf_count / self.N) * 100,
            'QF_%': (qf_count / self.N) * 100,
            'R16_%': (r16_count / self.N) * 100,
            'R32_%': (r32_count / self.N) * 100
        })
        
        results = results.sort_values(by='Win_%', ascending=False).reset_index(drop=True)
        return results

if __name__ == "__main__":
    teams_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'nation_strength_matrix.csv')
    draw_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'group_stage_draw.csv')
    
    engine = VectorizedMonteCarloEngine(num_simulations=25000)
    engine.load_data(teams_path, draw_path)
    
    print("Running 25,000 Monte Carlo Tournament Simulations...")
    results = engine.run_tournaments()
    
    print("\n==================================================")
    print("TOURNAMENT CHAMPION ODDS (Top 10)")
    print("==================================================")
    print(results.head(10))
    
    out_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
    results.to_csv(os.path.join(out_dir, 'monte_carlo_results.csv'), index=False)
