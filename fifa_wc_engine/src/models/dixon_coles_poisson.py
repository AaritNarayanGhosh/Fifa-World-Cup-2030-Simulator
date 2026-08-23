import numpy as np
import pandas as pd
from scipy.stats import poisson

class DixonColesMatchEngine:
    def __init__(self, team_matrix_path, base_goals=1.35, rho=0.15):
        """
        rho is the Dixon-Coles correlation parameter for low-scoring draws.
        Historically ~0.15 for international tournaments.
        """
        self.teams_df = pd.read_csv(team_matrix_path)
        self.teams_df.set_index('Nation', inplace=True)
        self.base_goals = base_goals
        self.rho = rho
        
        self.att_global_mean = self.teams_df['Att_Strength'].mean()
        self.def_global_mean = self.teams_df['Def_Strength'].mean()

    def get_lambdas(self, team_a, team_b, neutral=True):
        """
        Calculates expected goals (lambda) for Team A and Team B.
        """
        att_a = self.teams_df.loc[team_a, 'Att_Strength']
        def_a = self.teams_df.loc[team_a, 'Def_Strength']
        att_b = self.teams_df.loc[team_b, 'Att_Strength']
        def_b = self.teams_df.loc[team_b, 'Def_Strength']
        
        # lambda_A = Base_Goals * (Att_A / Att_Global_Mean) * (Def_Global_Mean / Def_B)
        # Note: A higher Def_B means better defense, so we divide by Def_B. 
        # (Wait, if Def_B is higher, (Def_Global / Def_B) is < 1, which reduces lambda_A. Correct.)
        lambda_a = self.base_goals * (att_a / self.att_global_mean) * (self.def_global_mean / def_b)
        lambda_b = self.base_goals * (att_b / self.att_global_mean) * (self.def_global_mean / def_a)
        
        return lambda_a, lambda_b
        
    def _tau(self, x, y, lambda_a, lambda_b):
        """
        Dixon-Coles adjustment factor for low-scoring matches.
        """
        if x == 0 and y == 0:
            return 1 - lambda_a * lambda_b * self.rho
        elif x == 0 and y == 1:
            return 1 + lambda_a * self.rho
        elif x == 1 and y == 0:
            return 1 + lambda_b * self.rho
        elif x == 1 and y == 1:
            return 1 - self.rho
        else:
            return 1.0

    def calc_score_probabilities(self, team_a, team_b, max_goals=10):
        """
        Generates a matrix of probabilities for all scores up to max_goals.
        """
        lambda_a, lambda_b = self.get_lambdas(team_a, team_b)
        
        prob_matrix = np.zeros((max_goals, max_goals))
        for x in range(max_goals):
            for y in range(max_goals):
                p_x = poisson.pmf(x, lambda_a)
                p_y = poisson.pmf(y, lambda_b)
                prob_matrix[x, y] = self._tau(x, y, lambda_a, lambda_b) * p_x * p_y
                
        # Normalize in case sum is slightly off from 1 due to truncation
        prob_matrix = prob_matrix / prob_matrix.sum()
        return prob_matrix
        
    def simulate_match(self, team_a, team_b):
        """
        Simulates a single match based on the probability matrix.
        Returns the score (goals_a, goals_b).
        """
        prob_matrix = self.calc_score_probabilities(team_a, team_b)
        flat_probs = prob_matrix.flatten()
        idx = np.random.choice(len(flat_probs), p=flat_probs)
        goals_a, goals_b = np.unravel_index(idx, prob_matrix.shape)
        return int(goals_a), int(goals_b)

if __name__ == "__main__":
    import os
    matrix_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed', 'nation_strength_matrix.csv')
    
    if os.path.exists(matrix_path):
        engine = DixonColesMatchEngine(matrix_path)
        team1 = "Spain"
        team2 = "Uruguay"
        
        print(f"Simulating Match: {team1} vs {team2}")
        l_a, l_b = engine.get_lambdas(team1, team2)
        print(f"Expected Goals (xG): {team1} {l_a:.2f} - {l_b:.2f} {team2}")
        
        # Simulate 100 matches to find probabilities
        results = {'A_Win': 0, 'Draw': 0, 'B_Win': 0}
        for _ in range(10000):
            g_a, g_b = engine.simulate_match(team1, team2)
            if g_a > g_b:
                results['A_Win'] += 1
            elif g_a == g_b:
                results['Draw'] += 1
            else:
                results['B_Win'] += 1
                
        print("\nMonte Carlo 10k Iterations Odds:")
        print(f"{team1} Win: {results['A_Win']/100:.1f}%")
        print(f"Draw: {results['Draw']/100:.1f}%")
        print(f"{team2} Win: {results['B_Win']/100:.1f}%")
